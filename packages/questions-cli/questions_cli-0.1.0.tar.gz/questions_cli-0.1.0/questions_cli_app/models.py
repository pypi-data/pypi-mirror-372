from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime
import hashlib

class AnswerOption(BaseModel):
    sNo: str
    option: str
    select: bool = False
    color: Optional[str] = None
    answerStatus: bool = False

class DetailedExplanation(BaseModel):
    options: Dict[str, str] = Field(default_factory=dict)

class QuestionDoc(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    topicId: Optional[str]
    topic: str
    topicHash: Optional[str]
    question: str
    answer: List[AnswerOption]
    explanation: Optional[str] = None
    validity: bool = True
    difficulty_level: Optional[str] = None
    concept1: Optional[str] = ""
    concept2: Optional[str] = ""
    concept3: Optional[str] = ""
    question_type: str = "multiple_choice"
    cognitive_level: Optional[str] = "understand"
    hints: List[str] = Field(default_factory=list)
    trivia: List[str] = Field(default_factory=list)
    primary_concept_tested: Optional[str] = ""
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    accepted_long_answer: Optional[str] = None
    detailed_explanation: Optional[DetailedExplanation] = None

class TopicDoc(BaseModel):
    id: Optional[str] = Field(None, alias="_id")
    topic: str
    definition: Optional[str]
    subject: Optional[str] = None
    core: bool = False
    subjectIllustrations: List[str] = Field(default_factory=list)
    subjectColor: Optional[str] = None
    department: Optional[str] = None
    createdAt: Optional[datetime] = None
    updatedAt: Optional[datetime] = None
    topic_hash: Optional[str] = None
    chapterName: Optional[str] = None
    timestamp: Optional[float] = None
