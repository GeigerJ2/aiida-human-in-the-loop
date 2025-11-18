import random
from typing import Optional

from aiida.engine import WorkChain, while_
from aiida.orm import Int, Dict


class HumanLoopWorkChain(WorkChain):
    @classmethod
    def define(cls, spec):
        super().define(spec)
        spec.input("max_iters", valid_type=Int, required=False, default=lambda: Int(20))
        spec.outline(
            cls.setup,
            while_(cls.not_finished)(
                cls.ask_and_pause,
                cls.process_answer,
            ),
            cls.finish,
        )
        spec.output("result", valid_type=Dict, required=False)

    def setup(self):
        # initialize once
        if not getattr(self.ctx, "inited", False):
            self.ctx.target = random.randint(1, 100)
            self.ctx.attempts = 0
            self.ctx.history = []
            self.ctx.last_guess = None
            self.ctx.inited = True
            self.ctx.finished = False
            self.ctx.question = "Guess a number between 1 and 100."
            self.report("initialized (target hidden)")

    def not_finished(self) -> bool:
        # loop predicate
        return not bool(
            getattr(self.ctx, "finished", False)
        ) and self.ctx.attempts < int(self.inputs.max_iters)

    def ask_and_pause(self):
        # publish a question visible as an extra
        self.node.base.extras.set("question", self.ctx.question)
        self.report(f"asked: {self.ctx.question!r}")
        # self.node.base.attributes.set('process_status', 'need user input')
        self.pause()

    def on_paused(self, msg: Optional[str] = None) -> None:
        """The process was paused."""
        super().on_paused(msg)
        if self.node.base.extras.get("question", None) is not None:
            self.node.set_process_status(
                'Need user input via "answer" extra before replaying!'
            )

    def process_answer(self):
        # read and consume answer
        # self.node.base.attributes.set('process_status', '')
        self.node.set_process_status("processing answer")
        self.report(f"Checking answer... (attempt {self.ctx.attempts})")
        raw = self.node.base.extras.get("answer", None)
        if raw is None:
            self.report(f"No answer found!")
            return
        # Clear answer to avoid re-processing
        self.report(f"Answer: {raw!r}. Clearing it...")
        self.node.base.extras.set("answer", None)

        self.report(f"Answer cleared. Parsing as an integer...")
        # parse
        try:
            guess = int(raw)
        except Exception:
            self.report(
                f"Invalid answer {raw!r}; please set an integer in extra 'answer'"
            )
            return

        self.report(f"Answer parsed as integer: {guess}")

        self.ctx.attempts += 1
        self.ctx.last_guess = guess

        if guess == self.ctx.target:
            self.ctx.history.append({"guess": guess, "feedback": "correct"})
            self.report(f"Attempt {self.ctx.attempts}: {guess} — CORRECT")
            self.node.base.extras.set(
                "question",
                f"Correct! The number was {guess}. Attempts: {self.ctx.attempts}. Finished!",
            )
            self.ctx.finished = True
            self.out(
                "result",
                Dict(
                    {
                        "message": f"Found {guess} in {self.ctx.attempts} attempts",
                        "history": self.ctx.history,
                    }
                ).store(),
            )
            return

        feedback = "higher" if guess < self.ctx.target else "lower"
        self.ctx.history.append({"guess": guess, "feedback": feedback})
        self.report(f"Attempt {self.ctx.attempts}: {guess} — answer is {feedback}")

        self.ctx.question = f"My number is {feedback} than {guess}. Try again."
        # Will be set as a question in the extras in the next loop iteration.

    def finish(self):
        if not getattr(self.ctx, "finished", False):
            self.report(
                f"finished without finding the number in {self.ctx.attempts} attempts"
            )
            self.node.base.extras.set(
                "question",
                f"Stopped after {self.ctx.attempts} attempts. (target hidden)",
            )
            self.out(
                "result",
                Dict(
                    {
                        "message": f"Failed after {self.ctx.attempts} attempts",
                        "history": self.ctx.history,
                    }
                ).store(),
            )
