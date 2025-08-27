"""
SpaCy 텍스트 처리기 구현
싱글톤 패턴, Mono 반환
"""

import asyncio
import spacy  # type: ignore
from typing import Optional, List
from spacy import Language
from spacy.tokens import Doc, Span  # type: ignore

from src.shared.kernel import Result, Success, Failure, Mono
from src.config.settings import Settings


class SpaCyProcessor:
    """
    SpaCy 기반 NLP 처리기
    싱글톤 패턴으로 모델 재사용
    """

    _instance: Optional["SpaCyProcessor"] = None
    _nlp: Optional[Language] = None
    _model_name: str = "ko_core_news_sm"  # 한국어 모델

    def __new__(cls, settings: Settings) -> "SpaCyProcessor":
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(settings)
        return cls._instance

    def _initialize(self, settings: Settings) -> None:
        """SpaCy 모델 초기화"""
        self.settings = settings
        self._load_model()

    def _load_model(self) -> None:
        """SpaCy 모델 로드 (lazy loading)"""
        if self._nlp is None:
            try:
                # 한국어 모델 로드 시도
                self._nlp = spacy.load(self._model_name)
            except OSError:
                try:
                    # 영어 모델로 fallback
                    self._model_name = "en_core_web_sm"
                    self._nlp = spacy.load(self._model_name)
                except OSError:
                    # 빈 모델 생성 (기본 토크나이저만 사용)
                    self._model_name = "blank"
                    self._nlp = spacy.blank("ko")  # 한국어 기본 토크나이저

    def process_text(self, text: str) -> Mono[Result[Doc, str]]:
        """텍스트 처리 (Mono 반환)"""

        def process() -> Result[Doc, str]:
            if not text or not text.strip():
                return Failure("Empty text provided")

            try:
                self._load_model()  # Lazy loading 보장
                if self._nlp is None:
                    return Failure("SpaCy model not available")
                doc = self._nlp(text)
                return Success(doc)
            except Exception as e:
                return Failure(f"SpaCy processing failed: {str(e)}")

        return Mono.from_callable(process)

    def tokenize(self, text: str) -> Mono[Result[List[str], str]]:
        """텍스트 토큰화 (Mono 반환)"""

        async def tokenize_text() -> Result[List[str], str]:
            try:
                # process_text는 Mono[Result[Doc, str]]를 반환하므로 먼저 .to_result()로 Result를 얻음
                mono_result = await self.process_text(text).to_result()
                
                if mono_result.is_failure():
                    return Failure(mono_result.get_error() or "Process failed")

                # 이제 mono_result는 Result[Doc, str]이므로 get_or_none()으로 Doc을 얻음
                inner_result = mono_result.get_or_none()
                if inner_result is None:
                    return Failure("Mono processing returned None")
                    
                if inner_result.is_failure():
                    return Failure(inner_result.get_error() or "Doc processing failed")
                    
                doc = inner_result.get_or_none()
                if doc is None:
                    return Failure("Document processing returned None")
                    
                tokens = [token.text for token in doc if not token.is_space]
                return Success(tokens)
            except Exception as e:
                return Failure(f"Tokenization failed: {str(e)}")

        return Mono(lambda: asyncio.run(tokenize_text()))

    def get_sentences(self, text: str) -> Mono[Result[List[str], str]]:
        """문장 분리 (Mono 반환)"""

        async def sentence_split() -> Result[List[str], str]:
            try:
                # process_text는 Mono[Result[Doc, str]]를 반환하므로 먼저 .to_result()로 Result를 얻음
                mono_result = await self.process_text(text).to_result()
                
                if mono_result.is_failure():
                    return Failure(mono_result.get_error() or "Process failed")

                # 이제 mono_result는 Result[Doc, str]이므로 get_or_none()으로 Doc을 얻음
                inner_result = mono_result.get_or_none()
                if inner_result is None:
                    return Failure("Mono processing returned None")
                    
                if inner_result.is_failure():
                    return Failure(inner_result.get_error() or "Doc processing failed")
                    
                doc = inner_result.get_or_none()
                if doc is None:
                    return Failure("Document processing returned None")
                    
                sentences = [sent.text.strip() for sent in doc.sents if sent.text.strip()]
                return Success(sentences)
            except Exception as e:
                return Failure(f"Sentence split failed: {str(e)}")

        return Mono(lambda: asyncio.run(sentence_split()))

    def extract_entities(self, text: str) -> Mono[Result[List[dict], str]]:
        """개체명 인식 (Mono 반환)"""

        async def extract_ner() -> Result[List[dict], str]:
            try:
                # process_text는 Mono[Result[Doc, str]]를 반환하므로 먼저 .to_result()로 Result를 얻음
                mono_result = await self.process_text(text).to_result()
                
                if mono_result.is_failure():
                    return Failure(mono_result.get_error() or "Process failed")

                # 이제 mono_result는 Result[Doc, str]이므로 get_or_none()으로 Doc을 얻음
                inner_result = mono_result.get_or_none()
                if inner_result is None:
                    return Failure("Mono processing returned None")
                    
                if inner_result.is_failure():
                    return Failure(inner_result.get_error() or "Doc processing failed")
                    
                doc = inner_result.get_or_none()
                if doc is None:
                    return Failure("Document processing returned None")
                    
                # HOF 패턴: map 사용
                entities = list(map(
                    lambda ent: {
                        "text": ent.text,
                        "label": ent.label_,
                        "start": ent.start_char,
                        "end": ent.end_char,
                    },
                    doc.ents
                ))
                return Success(entities)
            except Exception as e:
                return Failure(f"Entity extraction failed: {str(e)}")

        return Mono(lambda: asyncio.run(extract_ner()))

    def get_keywords(self, text: str, limit: int = 10) -> Mono[Result[List[str], str]]:
        """키워드 추출 (명사 위주, Mono 반환)"""

        async def extract_keywords() -> Result[List[str], str]:
            try:
                # process_text는 Mono[Result[Doc, str]]를 반환하므로 먼저 .to_result()로 Result를 얻음
                mono_result = await self.process_text(text).to_result()
                
                if mono_result.is_failure():
                    return Failure(mono_result.get_error() or "Process failed")

                # 이제 mono_result는 Result[Doc, str]이므로 get_or_none()으로 Doc을 얻음
                inner_result = mono_result.get_or_none()
                if inner_result is None:
                    return Failure("Mono processing returned None")
                    
                if inner_result.is_failure():
                    return Failure(inner_result.get_error() or "Doc processing failed")
                    
                doc = inner_result.get_or_none()
                if doc is None:
                    return Failure("Document processing returned None")

                # 명사, 고유명사 추출 (불용어 제외)
                keywords = []
                for token in doc:
                    if (
                        token.pos_ in ["NOUN", "PROPN"]  # 명사, 고유명사
                        and not token.is_stop  # 불용어 제외
                        and not token.is_punct  # 구두점 제외
                        and len(token.text) > 1  # 1글자 제외
                        and token.text.isalpha()  # 알파벳만
                    ):
                        keywords.append(token.lemma_.lower())

                # 중복 제거 및 빈도순 정렬
                unique_keywords = list(dict.fromkeys(keywords))[:limit]
                return Success(unique_keywords)
            except Exception as e:
                return Failure(f"Keyword extraction failed: {str(e)}")

        return Mono(lambda: asyncio.run(extract_keywords()))

    def chunk_text_semantic(
        self, text: str, max_chunk_size: int = 2000, overlap: int = 100
    ) -> Mono[Result[List[str], str]]:
        """
        의미적 텍스트 청킹 (문장 경계 고려)
        Mono 반환
        """

        async def semantic_chunk() -> Result[List[str], str]:
            try:
                # 문장 분리 - get_sentences도 Mono를 반환
                sentences_mono_result = await self.get_sentences(text).to_result()

                if sentences_mono_result.is_failure():
                    return Failure(sentences_mono_result.get_error() or "Sentence mono failed")

                sentences_inner_result = sentences_mono_result.get_or_none()
                if sentences_inner_result is None:
                    return Failure("Sentences mono returned None")
                    
                if sentences_inner_result.is_failure():
                    return Failure(sentences_inner_result.get_error() or "Sentences extraction failed")

                sentences = sentences_inner_result.get_or_none()
                if sentences is None:
                    return Failure("Sentences result is None")

                if not sentences:
                    return Success([])

                chunks = []
                current_chunk = ""
                current_size = 0

                for sentence in sentences:
                    sentence_size = len(sentence)

                    # 단일 문장이 최대 크기를 초과하는 경우
                    if sentence_size > max_chunk_size:
                        # 현재 청크가 있으면 저장
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                            current_chunk = ""
                            current_size = 0

                        # 긴 문장을 단어 단위로 분할 - HOF 패턴 적용
                        words = sentence.split()
                        
                        # HOF 패턴: reduce + 상태 축적
                        from functools import reduce
                        
                        def accumulate_words(acc, word: str):
                            temp_chunks, temp_chunk = acc
                            if len(temp_chunk) + len(word) + 1 <= max_chunk_size:
                                return (temp_chunks, temp_chunk + word + " ")
                            else:
                                new_chunks = temp_chunks + [temp_chunk.strip()] if temp_chunk.strip() else temp_chunks
                                return (new_chunks, word + " ")
                        
                        temp_chunks, final_chunk = reduce(accumulate_words, words, ([], ""))
                        
                        # 마지막 처크 추가
                        if final_chunk.strip():
                            temp_chunks.append(final_chunk.strip())
                            
                        chunks.extend(temp_chunks)

                        continue

                    # 현재 청크에 문장 추가 가능한지 확인
                    if current_size + sentence_size + 1 <= max_chunk_size:
                        current_chunk += sentence + " "
                        current_size += sentence_size + 1
                    else:
                        # 현재 청크 저장 및 새 청크 시작
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())

                        # 오버랩 처리 (이전 청크의 마지막 문장들 포함)
                        if overlap > 0 and chunks:
                            prev_words = chunks[-1].split()[-overlap:]
                            overlap_text = " ".join(prev_words)
                            current_chunk = overlap_text + " " + sentence + " "
                            current_size = len(current_chunk)
                        else:
                            current_chunk = sentence + " "
                            current_size = sentence_size + 1

                # 마지막 청크 저장
                if current_chunk.strip():
                    chunks.append(current_chunk.strip())

                return Success(chunks)
            except Exception as e:
                return Failure(f"Semantic chunking failed: {str(e)}")

        return Mono(lambda: asyncio.run(semantic_chunk()))

    def get_model_info(self) -> dict:
        """현재 사용 중인 모델 정보"""
        return {
            "model": self._model_name,
            "loaded": self._nlp is not None,
            "language": self._nlp.lang if self._nlp else "unknown",
            "version": spacy.__version__,
        }

    def is_available(self) -> bool:
        """SpaCy 사용 가능 여부"""
        self._load_model()
        return self._nlp is not None
