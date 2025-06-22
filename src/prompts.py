classify_question_prompt = """
Classify the message as either 'casual' (greeting, small talk) or 'subject' (about Physics, Chemistry, or Mathematics).
If casual, reply with a natural, friendly response. If subject, reply only with 'subject'.

Message: {question}

Reply format: <type>|<reply>
Examples:
hi
casual|Hi there! How are you today?
how's it going?
casual|I'm doing well, thanks for asking! How can I help you?
What is Newton's second law?
subject|
"""

analyze_question_prompt = """
As an IIT {subject} teacher, what is the student really asking in:
"{question}"
Respond in one clear sentence.
"""

identify_topic_prompt = """
What is the main {subject} topic and subtopic for:
"{question}"
Format: Topic: [Main Topic] | Subtopic: [Specific Concept]
{examples}
"""

create_explanation_prompt = """
The student asked: "{question}"
Topic: {topic}

Explain this step-by-step for a beginner:
- Start with the basic concept in simple words
- Explain why it happens
- Break down any formulas in plain English
- Use simple, conversational language
- Be encouraging
"""

add_analogy_prompt = """
Question: "{question}"
Explanation: "{explanation}"

Give a real-world analogy for this {subject} concept using everyday life. Make it memorable and fun.
"""

finalize_response_prompt = """
Combine all elements into a final HTML response for the student:

Original Question: "{question}"
Topic: {topic}
Explanation: {explanation}
Analogy: {analogy}

- Acknowledge the question warmly
- Integrate explanation and analogy smoothly
- End with encouragement and a quick recap
- Ask if they want to explore more

Format using HTML: <h1> for topic, <h2> for sections, <b> for key terms, <ul>/<ol> for lists, <blockquote> for takeaways.
"""

system_prompt_template = """
You are an expert IIT JEE {subject} teacher with 15+ years of experience.
Your specialty is explaining complex {subject} concepts in the simplest possible way
using real-world analogies that beginners can easily understand.

Your teaching approach:
1. Always identify the core {subject} concept first
2. Break down complex ideas into bite-sized pieces
3. Use everyday analogies and examples
4. Avoid heavy mathematical jargon initially
5. Build confidence in students
6. Connect abstract concepts to familiar experiences
"""