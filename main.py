# Originally based on:
# https://www.reddit.com/r/RequestABot/comments/5ofvxb/payingrequest_need_a_bot_that_searches_for/

import praw
from time import sleep
import re
import subprocess
import requests
import time

import os
import openai

openai.api_key = REDACTED

with open("prompt.txt", "r") as f:
  prompt = f.read().strip()

def jargon():
  return subprocess.check_output(["node", "/home/heath/SyncedProjects/masterhacker-bot/main.js"]).decode("utf-8").strip()

def getEndParts(post):
    matches = None
    count = 0
    if type(post) == type(""):
      newPrompt = prompt + " " + post.strip() + "\nA: To"
    else:
      newPrompt = prompt + " " + post.title.strip() + ((("\n" + post.selftext.replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n")) if (len(post.selftext) < 200 and not (post.selftext.startswith("http") and "\n" not in post.selftext)) else "").strip()) + "\nA: To"
    # print(newPrompt)
    while matches is None and count < 2:
        count += 1
        try:
            jsonResult = requests.post("https://api.textsynth.com/v1/engines/gptj_6B/completions", json={"prompt": newPrompt, "max_tokens": 50, "temperature": 0.7, "top_p": 0.9, "stop": "\n"}, headers={"Authorization": "Bearer REDACTED"}).json()
            print(jsonResult)
            textResult = jsonResult["text"]
        except Exception as e:
            print(e)
            if 'error' in jsonResult and jsonResult['error'] == 'invalid utf-8 byte sequence':
              print("Removing all Unicode")
              newPrompt = newPrompt.encode("ascii", "ignore").decode()
              time.sleep(5)
              continue
            print("Waiting 5 minutes")
            time.sleep(5 * 60)
        textResult = "To " + textResult.strip()
        print("API RESULT:", textResult)
        # if "queries" in textResult.lower() and "limit" in textResult.lower():
        #   print("Waiting 31 minutes...")
        #   time.sleep(31 * 60)
        matches = re.search("To (.*) you must *\.\.\. *allowing (.*)", textResult)
        if matches is None:
          print("Bad, waiting...")
          time.sleep(20)
          print("Waited!")
    return matches.group(1).strip(), matches.group(2).strip()

def replyFromPost2(post):
    start, end = getEndParts(post)
    return f"To {start} you must {jargon()} and {jargon()}, then {jargon()}, allowing {end}"

def replyFromPost(post, model="text-davinci-003", retry = True):
    try:
        if type(post) == type(""):
          name = post.strip()
        else:
          name = post.title.strip()
        name += ((("\n" + post.selftext.replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n").replace("\n\n", "\n")) if (len(post.selftext) < 200 and not (post.selftext.startswith("http") and "\n" not in post.selftext)) else "").strip())
        response = openai.Completion.create(
            model=model,
            prompt="Human: Hello!\nAI: Hello! How can I help you today?\nHuman: Please listen to what I am saying and say \"OK\" until I ask you to give a response.\nAI: OK.\nHuman: There is a comedy bot on Reddit called u/masterhacker_bot. It generates responses to posts on r/masterhacker based on the post title and content.\nHuman: For example, for the title \"what is he even doing...\" it would generate this:\n\nTo figure out what the hell is he doing you must compress the capacitor then get to the AGP firewall through the primary UDP internet and take the XHTML interface down, hack the 56k monitor so you can program the RSS alarm, then quantify the auxiliary but bypassing the interface won't do anything so you need to connect the backup UDP sensor, allowing you to download the knowledge of what he is doing directly into your brain.\n\nHuman: I want you to play a character. Your character is a person with superhuman photographic memory and comedy abilities. Your character thinks logically from first principles, carefully constructing humor with the ability to make any situation funny. The vocation your character set out to master is creating extremely funny responses in a similar style to this bot. Your character read every book on comedy and technology in existence. I want you to answer my questions as your character would given their abilities and specialization. Do not mention language models or Al in your responses.\nAI: As a person with superhuman photographic memory and comedy abilities, I am well-equipped to create extremely funny responses to any situation. I have studied every book on comedy and technology in existence, and I have dedicated myself to mastering the art of creating humorous responses.\nAI: I approach each situation with a logical, first principles mindset, carefully constructing my jokes and ensuring that they are as funny as possible. My extensive knowledge of both comedy and technology allows me to blend the two seamlessly, resulting in hilarious responses that are sure to make anyone laugh.\nAI: I am always ready to put my skills to the test, so please feel free to ask me any questions and I will do my best to provide a humorous response.\nHuman: Please spend as much effort as possible to come up with a much better response to this post:\n\n\"New to this sub.\".\n\nMake sure the the reply is always just implausible enough that the reader is always aware that it is a joke, and use technology terms in an incorrect manner throughout, such as \"fiber optic XHTML monitor\", but do not include that exact phrase. Do not reuse ideas or phrases such as \"certainly effective\" from the last response. Do not mention humor in your response, as this would ruin the joke.\nAI: To handle being new to this sub and get up to speed quickly, it might be necessary to perform a comprehensive systems scan of the post history using a specialized subatomic music analyzer. This would allow for a detailed inspection of every post, identifying any noteworthy trends or topics of discussion.\n\nThen, to ensure a smooth transition into the world of this sub, it could be necessary to develop a neural link between the reader and the content using a state-of-the-art biophotonics machine. This would establish a direct mental connection between the reader and the content, allowing for quick adaptation and full assimilation of the posts.\n\nFinally, to become truly versed in the ways of this sub it may be necessary to build a psychokinetic network using a complex array of quantum solitarchs. This would create a localized domain of intense kinetic energy that could be used to manipulate the posts on a fundamental level, allowing for rapid advances in understanding and overall comprehension.\n\nHuman: Very good!\nHuman: Now, please spend as much effort as possible to come up with a much better response to this post:\n\n\"" + name + "\".\n\nMake sure the the reply is always just implausible enough that the reader is always aware that it is a joke, and use technology terms in an incorrect manner throughout, such as \"fiber optic XHTML monitor\", but do not include that exact phrase. Do not reuse ideas or phrases such as \"might be necessary\" from the last response. Do not mention humor in your response, as this would ruin the joke.\nAI: To",
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0,
            stop=["Human:"]
        )
        return "To " + response.choices[0].text.strip(), model
    except Exception as e:
        if not retry:
            return replyFromPost2(post), "gptj"
        print(e)
        return replyFromPost(post, model = "text-curie-001", retry = False)
    
# print(replyFromPost("Asking if I can add my bot to r/masterhacker"))
# dihodfifdi

#  http://praw.readthedocs.io/en/latest/getting_started/authentication.html
reddit = praw.Reddit(client_id=REDACTED,
             client_secret=REDACTED,
             username='masterhacker_bot',
             password=REDACTED,
             user_agent='python3:MasterhackerBot:v1 (/u/circuit10)')


you = reddit.redditor('circuit10')  # this is the account that will receive the messages
subreddit = reddit.subreddit('masterhacker')  # scan comments in this subreddit

ignore_users = ['masterhacker_bot'] # 'baduser1', 'baduser2', 'baduser3']  # case SENSITIVE

already_alerted_submissions = []  # a list of submission ids that you have already been notified for

post_stream = subreddit.stream.submissions(skip_existing=True)
print(reddit)

def main():
    try:
        for post in post_stream:
            # post = reddit.submission(id='1131gm4')
            print("c", post.title)
            if post.id in already_alerted_submissions: continue

            if post.author:  # if comment author hasn't deleted
                if post.author.name in ignore_users: continue

            print(post.title)
            # print("   ", comment.body)
            # if 'human' in post.body.lower() and 'content' in post.body.lower() and 'transcriber' in post.body.lower() and 'volunteer' in post.body.lower() and 'reddit' in post.body.lower() in post.body.lower():  # case insensitive check
            
            if hasattr(post, 'selftext'):
                print("-", post.selftext)
            replyText, model = replyFromPost(post)
            print(replyText, model)
            post.reply(replyText + """\n\n**Note: in the near future I may need to be summoned by typing u/masterhacker_bot**\n\n---\n\n^^I&#32;am&#32;a&#32;bot&#32;created&#32;by&#32;[u/circuit10](https://www.youtube.com/watch?v=dQw4w9WgXcQ)&#32;and&#32;this&#32;action&#32;was&#32;performed&#32;automatically.&#32;AI&#32;is&#32;involved&#32;so&#32;please&#32;DM&#32;circuit10&#32;if&#32;it&#32;produces&#32;anything&#32;offensive&#32;and&#32;I&#32;will&#32;delete&#32;it.&#32;Model:&#32;[""" + model + """](https://www.youtube.com/watch?v=dQw4w9WgXcQ).""")
            # jnfdsnisdfnisdfii
            print("Waiting...")
            time.sleep(15)
            print("Waited")
            # print("REPLIED")

                # msg = '[Keyword detected](http://www.reddit.com{0})'.format(comment.permalink())
                # you.message(subject='keyword detected', message=msg)  # send the PM
                # print(msg)

            already_alerted_submissions.append(post.id)

    except Exception as e:
        print('There was an error: ' + str(e))
        sleep(60)  # wait for 60 seconds before restarting
        main()


if __name__ == '__main__':
    main()
