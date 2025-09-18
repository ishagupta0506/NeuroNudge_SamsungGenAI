from langchain_openai import ChatOpenAI
from langchain.prompts.prompt import PromptTemplate
from langchain.output_parsers.pydantic import PydanticOutputParser
from langchain.output_parsers.structured import StructuredOutputParser
from langchain.output_parsers import OutputFixingParser
from pydantic import BaseModel, Field
import os


llm = ChatOpenAI(model_name="gpt-4o-mini", temperature=1) 
class TaskPlan(BaseModel):
    task_plans: list[str] = Field(..., description="A detailed NeuroNudge-friendly task plans.")

output_parser = PydanticOutputParser(pydantic_object=TaskPlan)

retry_parser = OutputFixingParser.from_llm(parser=output_parser, llm=llm)

prompt = PromptTemplate(template="""
You are an expert neuropsychologist and productivity coach specialized in creating NeuroNudge-friendly task plan of total 25-minute session.
               
I will give you a high-level task. Break it into a **NeuroNudge-friendly task plan**  with the following structure:

1. **Tiny Steps First:** Start with the absolute *smallest possible action*  to overcome activation energy.
2. **Phase Grouping:** Organize subtasks into friendly phases (e.g., *Warm-up, Explore, Build, Polish, Share* or better anything).
3. **Time Bites:** Suggest rough time ranges in **focus-friendly chunks** (10–25 mins).
4. **Nudges:** For each step, include a short **NeuroNudge tip** — motivational, low-pressure, and progress-oriented .
5. **Celebrate & Reset:** After each phase, add a *micro-reward suggestion* (stretch, music, snack, note to self).
6. **Output Format:**

   * Hierarchical  list
   * Each subtask = action + (time bite) + NeuroNudge tip(if needed)

---
🎉 Reward: Take a 5-min break, stretch, or jot down “Intro draft = done.”

**Now, create a NeuroNudge-friendly task plan for this:** without any additional commentary and only subtasks without numbering with limited to 5 so that user don't feel overwhelmed.
                        
### Task Description: 
============================= 
{task_description}
============================= 
### Output Format:
============================= 
{output_format}    
=============================
""",input_variables=["task_description"],partial_variables={
    "output_format": retry_parser.get_format_instructions()
})


task_chain = prompt | llm | retry_parser


def generate_task_plan(task_description: str) -> list[str]:
   
    response = task_chain.invoke({
        "task_description": task_description
    }).task_plans
    return response


def generate_nudge(mood:str)->str:

    prompt_for_nudge = PromptTemplate(template="""
    You are an expert neuropsychologist and productivity coach.
   Generate one short, supportive NeuroNudge (1–2 sentences) that feels friendly for ADHD brains. Each time, vary the angle — it could be about starting small, celebrating progress, reframing perfectionism, using time chunks, energy check-ins, environment tweaks, or self-compassion. Avoid repeating the same theme in consecutive nudges. you can use metaphors, humor, or relatable scenarios to make it engaging. Keep it light, positive, and actionable.
   Tailor the nudge to the user's current mood and use emojis to make it more relatable if needed.
                            
    ### Mood: {mood}
    ============================= 
   without any additional commentary and only nudge.
    """,input_variables=["mood"])


    task_chain_for_nudge = prompt_for_nudge | ChatOpenAI(model_name="gpt-4o-mini", temperature=1)  
    return task_chain_for_nudge.invoke({"mood": mood}).content


def get_emotion_llm(description:str)->str:
    prompt_for_emotion = PromptTemplate(template="""
You are an emotion classifier.  
Classify the emotion in the given description as exactly one of the following: sadness, joy, love, anger, fear, surprise.  
Respond with only the emotion word.

Examples:  
Input: "I just lost my favorite watch today."  
Output: sadness  

Input: "She hugged me tightly after a long time apart."  
Output: love  

Input: "They gave me a surprise party for my birthday!"  
Output: surprise  

Input: "Someone cut me off in traffic and yelled at me."  
Output: anger  

Now classify the emotion for this description:  
{description}
    """,input_variables=["description"])


    task_chain_for_emotion = prompt_for_emotion | ChatOpenAI(model_name="gpt-4o-mini", temperature=1)  
    return task_chain_for_emotion.invoke({"description": description}).content.lower()

def get_music(emotion:str,music_types:list)->str:
    prompt_for_emotion_music = PromptTemplate(template="""
You are an expert at matching emotions with music. I will provide an emotion from this set: sadness, joy, love, anger, fear, surprise along with a list of possible music types. From the list, select the one music type that best matches the given emotion.
Emotion: {emotion}
Music Types: {music_types}
 Respond only with the chosen music type, we will be using that as dictionary key to get music, nothing else.
    """,input_variables=["emotion","music_types"])


    task_chain_for_emotion_music = prompt_for_emotion_music | ChatOpenAI(model_name="gpt-4o-mini", temperature=1)  
    return task_chain_for_emotion_music.invoke({"emotion":emotion,"music_types":music_types}).content