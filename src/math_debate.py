# Modified By Jiho Choi (jihochoi@kaist.ac.kr)


# References:
# https://github.com/composable-models/llm_multiagent_debate


import openai
import json
import numpy as np
import time
import datetime
import json
import pickle
import os
from tqdm import tqdm


from utils import ensure_directory
from utils import retrieve_openai_api_key
from utils import parse_answer
from utils import most_frequent_answer

# Usage:
# python ./src/math_debate.py


# os.environ["OPENAI_API_KEY"] = ("project-key")
OPENAI_API_KEY = retrieve_openai_api_key("./env/key.txt")
openai.api_key = OPENAI_API_KEY

print(f"--------------------------------")
print(f"OPENAI_API_KEY: {OPENAI_API_KEY}")
print(f"--------------------------------")


RESULTS_FILE = ""


def print_and_append_results(string):
    print(string)
    with open(RESULTS_FILE, "a") as output_file:
        output_file.write(str(string) + "\n")


def generate_answer(answer_context, max_tokens=200):
    try:
        completion = openai.ChatCompletion.create(
            model="gpt-3.5-turbo-0301",
            messages=answer_context,
            n=1,
            max_tokens=max_tokens,
        )
    except:
        # print("retrying due to an error......")
        # time.sleep(20)
        # return generate_answer(answer_context)
        print("Error: GPT")
        exit()
    return completion


def construct_assistant_message(completion):
    content = completion["choices"][0]["message"]["content"]
    return {"role": "assistant", "content": content}


def construct_message_reflection():
    # (p_r) Reflection Prompt
    message = "Can you verify that your answer is correct. Please reiterate your answer, making sure to state your answer at the end of the response."
    return {"role": "user", "content": message}


def construct_message_debate(agents, question, idx):
    # Use introspection in the case in which there are no other agents.
    if len(agents) == 0:
        print("Error: no other agents!")
        exit()

    # (p_r) Debate Prompt
    message = "These are the recent/updated opinions from other agents: "
    for agent in agents:
        response = f"\n\n One agent response: ```{agent[idx]["content"]}```"
        message = message + response
    message = (
        message
        + "\n\n Use these opinions carefully as additional advice, can you provide an updated answer? Make sure to state your answer at the end of the response.".format(
            question
        )
    )
    return {"role": "user", "content": message}


if __name__ == "__main__":

    current = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")

    ensure_directory("./results/")
    RESULTS_FILE = f"./results/debate_{current}.tex"

    agents = 3
    rounds = 2
    evaluation_round = 20
    evaluation_round = 10

    np.random.seed(0)
    scores = []

    generated_description = {}

    for round in tqdm(range(evaluation_round)):
        a, b, c, d, e, f = np.random.randint(0, 30, size=6)
        answer = a + b * c + d - e * f
        agent_contexts = [
            [
                {
                    "role": "user",
                    "content": f"What is the result of {a}+{b}*{c}+{d}-{e}*{f}? Make sure to state your answer at the end of the response.",
                }
            ]
            for agent in range(agents)
        ]
        content = agent_contexts[0][0]["content"]
        question_prompt = \
            f"We seek to find the result of {a}+{b}*{c}+{d}-{e}*{f}?"

        print(f"----------------------------------")
        print(f"agent_contexts : {agent_contexts} ")
        print(f"question_prompt: {question_prompt}")
        print(f"----------------------------------")

        # ------------------
        # multi-agent debate
        # ------------------
        for round in range(rounds):
            for i, agent_context in enumerate(agent_contexts):

                if round != 0:
                    # [round 0] 을 제외하고는 모든 round에 다른 agent의 결과 취합
                    agent_contexts_other = agent_contexts[:i] + \
                        agent_contexts[i + 1:]
                    message = construct_message_debate(
                        agent_contexts_other, question_prompt, 2 * round - 1
                    )
                    agent_context.append(message)
                    print(f"agent {i} (input): {message}")

                completion = generate_answer(agent_context)
                assistant_message = construct_assistant_message(completion)
                print(f"[agent {i} (output)]: {assistant_message}")
                agent_context.append(assistant_message)
                # print("completion:", completion)

        # ---------------
        # self-reflection
        # ---------------
        for i, agent_context in enumerate(agent_contexts):
            message = construct_message_reflection()
            print(f"[agent {i} (input)]: {message}")
            agent_context.append(message)
            completion = generate_answer(agent_context)
            assistant_message = construct_assistant_message(completion)
            print(f"[agent {i} (output)]: {assistant_message}")
            agent_context.append(assistant_message)
            # print(completion)

        # ------------
        # parse answer
        # ------------
        text_answers = []
        for agent_context in agent_contexts:
            text_answer = agent_context[-1]["content"]
            text_answer = text_answer.replace(",", ".")
            text_answer = parse_answer(text_answer)
            if text_answer is None:
                continue
            text_answers.append(text_answer)
        generated_description[(a, b, c, d, e, f)] = (agent_contexts, answer)

        # ---------------
        # calculate score
        # ---------------
        print("text_answers:", text_answers)
        try:
            text_answer = most_frequent_answer(text_answers)
            if text_answer == answer:
                scores.append(1)
            else:
                scores.append(0)
        except:
            continue

        print(
            f"performance: {
                np.mean(scores)} +- {np.std(scores) / (len(scores) ** 0.5)}"
        )
        print(f"scores: {scores}")

    # Print
    print(f"-------------------------")
    print(f"generated_description: {generated_description}")
    print(f"-------------------------")
    print("------------------------------------------------------------------")
    for des in generated_description:
        print(f"des: {des}")
    print("------------------------------------------------------------------")

    # with open(f"./results/{run_name}.txt", "a") as file:
    #     file.write(json.dumps(generated_description))

    # pickle.dump(
    #     generated_description,
    #     open("math_agents{}_rounds{}.pkl".format(agents, rounds), "wb"),
    # )
    # import pdb

    # pdb.set_trace()
    print(f"--------------------------------")
    print(f"answer: {answer}")
    print(f"agent_contexts: {agent_contexts}")
    print(f"--------------------------------")
