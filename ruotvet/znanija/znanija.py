from ruotvet.request import Request
from .parser import Parser, Task
from dataclasses import replace
import typing


class Znanija:
    @staticmethod
    def get_answers(query: str, count: int = 5, offset: int = 0, language: str = "ru") -> typing.List[Task]:
        request = Request()
        parser = Parser()
        output = []

        url = f"https://www.google.com/search?q=site:znanija.com {query.lower()}&start={offset}&num={count}" \
              f"&ie=utf-8&oe=utf-8&lr=lang_{language}"

        answers = parser.parse_search_results(response=request.make("GET", url))
        for answer in answers:
            question_text, answer_text, attachment = parser.parse_question(request.make("GET", answer.url))
            output.append(replace(answer, **{"question": question_text, "answer": answer_text,
                                             "attachment": attachment}))
        return output

    @staticmethod
    def get_attachment(answer: Task) -> str:
        request = Request()
        response = request.make("GET", answer.attachment, stream=True)
        if response.status_code == 200:
            with open(f"media/{answer.url.split('task/')[1]}.jpg", "+wb") as file:
                file.write(response.content)
                file.close()
            return f"media/{answer.url.split('task/')[1]}.jpg"