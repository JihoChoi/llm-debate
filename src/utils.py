# Jiho Choi


# -----------------------------------------------------
# Utils
# -----------------------------------------------------


import os


def ensure_directory(path):
    path = os.path.split(path)
    if not os.path.exists(path[0]):
        os.makedirs(path[0])


def retrieve_openai_api_key(KEY_PATH="./env/key.txt"):
    with open(KEY_PATH, "r") as f:
        for line in f:
            if line.startswith(f"OPENAI_API_KEY="):
                return line.strip()[len("OPENAI_API_KEY=") :]


# -----------------------------------------------------
# Post Processing: Parse Answers, Retrieve Answers
# -----------------------------------------------------


def parse_answer(sentence):
    # 정답 : 마지막 float 변환 가능 문자
    parts = sentence.split(" ")
    for part in parts[::-1]:
        try:
            answer = float(part)
            return answer
        except:
            continue


def most_frequent_answer(List):
    counter = 0
    num = List[0]
    for i in List:
        current_frequency = List.count(i)
        if current_frequency > counter:
            counter = current_frequency
            num = i
    return num


if __name__ == "__main__":

    print("------------")
    print("    Test    ")
    print("------------" + "\n")


    print(
        parse_answer(
            "My answer is the same as the other agents and AI language model: \
                the result of 12+28*19+6 is 550."
        )
    )  # 555.0
    print(most_frequent_answer([246.0, 246.0, 50.0]))        # 246.0
    print(most_frequent_answer([50.0, 246.0, 50.0, 246.0]))  # 50.0

