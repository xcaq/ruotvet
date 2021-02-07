from ruotvet.http import AIOHTTPClient
from ruotvet.types import Question, Attachment
from typing import List, Optional, AsyncGenerator
from bs4 import BeautifulSoup


class SuperResheba:
    def __init__(self):
        self.client = AIOHTTPClient()
        self.parser = Parser()

    async def get_answers(self, query: str, count: int = 1) -> List[Question]:
        url = f"https://www.google.com/search?q=site:superresheba.by {query.lower()}&start=0&num={count}" \
              f"&ie=utf-8&oe=utf-8&lr=lang_ru"
        output = []
        try:
            async for question in self.parser.parse_search_results(await self.client.request_text("GET", url)):
                response = await self.parser.parse_question(await self.client.request_text("GET", question.url))
                if (response["question"] or response["answer"] or response["attachments"]) is not None:
                    output.append(question.copy(update=response))
            return output
        finally:
            await self.client.close()


class Parser:
    @staticmethod
    def prepare_text(text: str) -> str:
        output = []
        for word in text.rstrip(" ").split():
            output.append(word)
        return " ".join(output).capitalize()

    @staticmethod
    async def parse_search_results(response: str) -> AsyncGenerator[Optional[Question], None]:
        soup = BeautifulSoup(response, "html.parser")
        for iteration in soup.find_all(href=True):
            if iteration and iteration.findChildren("h3"):
                if iteration["href"].startswith("https"):
                    yield Question(url=iteration["href"])

    async def parse_question(self, response: str) -> Optional[dict]:
        soup = BeautifulSoup(response, "html.parser")
        question = soup.find("div", {"class": "article_header"})
        question = self.prepare_text(question.text) if question else None
        answer = soup.find_all("div", {"class": "single-part"}) or None
        images = soup.find("div", {"itemprop": "acceptedAnswer"}) or None
        attachments = []
        if answer:
            text = ""
            for part in answer:
                text += part.text
            answer = self.prepare_text(text)
        if images:
            for image in images.find_all("img"):
                image_src = str(image).split("../../")[1].split("\" width")[0]
                attachments.append(Attachment(url=f"https://superresheba.by/{image_src}"))
        return {"question": question, "answer": answer, "attachments": attachments or None}