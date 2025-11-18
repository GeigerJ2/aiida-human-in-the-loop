from aiida.orm import load_node
import sys
import time
from aiida.engine.processes import control

if __name__ == "__main__":
    wf = load_node(int(sys.argv[1]))

    while not wf.is_finished:
        while not wf.is_finished and not wf.paused:
            print("Workflow not paused yet, waiting...")
            time.sleep(2)
        if wf.is_finished:
            break
        question = wf.base.extras.get('question', 'No question found.')
        print("--------------------------------------------------")
        print(f"Question from workflow: '{question}'")
        answer = input("Your answer: ")
        wf.base.extras.set('answer', answer)
        control.play_processes([wf])
        print(f"Answer submitted and workflow replayed.")
        print("Waiting for next question...")

    print("==================================================")
    print("Workflow finished!")
    if 'result' in wf.outputs:
        print(f"Output message: {wf.outputs.result.value.get('message', 'No output message found.')}")
    else:
        print("No result output found.")

    print("History of attempts:")
    for attempt in wf.outputs.result.value.get('history', []):
        print(f"  {attempt}")

