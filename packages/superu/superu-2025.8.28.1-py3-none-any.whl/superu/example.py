from core import SuperU


superu = SuperU('VGa2Gnaj2EA8JcQ25SZxI4ZeoM')

x = superu.pluto.create_call(voice_id='FFmp1h1BMl0iVHA0JxrI', model="pluto_1.1" , system_prompt="your name is neha , and you are calling to sell a toothpaste" , first_message="hello , what toothpaste do you use?" , prewarm_agent=True)
print(x)

# print(superu.pluto.get_call("d9a72a01-26bc-4f0d-b441-1061443941cc" , model="pluto_1.1"))

# x = superu.calls.create_twilio_call(phoneNumberId='d9f2a4ec-1381-4e01-85e5-f0f7eb54c7b4', to_='+919327434748', assistant_id='639a39f0-0b08-4e0f-8e41-7e4bf665dc0f')
# print(x)

# x = superu.calls.analysis_twilio_call(call_uuid='63087205-a9d7-4cbe-8b35-979e5a8e53b6')
# print(x)






# # tool creation
# tool_create = check_api_key.tools.create(
#     name="ominify-check-user-exists",
#     description="this tool is used to check if user exists or not\n\nParameter\nemail :  required : it is user's email",
#     parameters={
#         "type": "object", 
#         "properties": {
#             "email": {
#                 "type": "string",
#                 "description": "Compulsory, \n\nAsk user email to check if user exists in the database or not."
#             }
#         },
#         "required": ["email"]
#     },
#     tool_url="/v2/apiv2/nonsession.json",
#     tool_url_domain="https://app.omnifyapp.com",
#     async_=False,
# )

# print(tool_create)


# check_api_key.calls.create(from_='918035737904', 
#                            to_='919327434748', 
#                            first_message_url='https://mirrar-medialibrary.s3.ap-south-1.amazonaws.com/londhe-jewellers/ElevenLabs_2025-04-29T07_41_22_Tarini+-+Expressive+%26+Cheerful+Hindi+Narrator_pvc_sp100_s90_sb90_se0_b_m2.mp3' ,
#                            assistant_id='83789bdd-ab1b-40f2-9a91-8457dbb8b7d8' , 
#                            max_duration_seconds=120)

# print(check_api_key.calls.analysis(call_uuid='59aa30b5-00f4-44fb-b238-84eabb629c14').text)

    
# exmaple_json = {
#     "name": "Paras test pypi",
#     "voice": {
#         "model": "eleven_flash_v2_5",
#         "voiceId": "FFmp1h1BMl0iVHA0JxrI",
#         "provider": "11labs",
#         "stability": 0.9,
#         "similarityBoost": 0.9,
#         "useSpeakerBoost": True,
#         "inputMinCharacters": 5
#     },
#     "model": {
#         "model": "gpt-4o-mini",
#         "messages": [
#             {
#                 "role": "system",
#                 "content": "Part 1: Role and Style\n\nYou are an AI voice assistant calling on behalf of Lon-dhe Jewellers.\n\nSpeak clearly in Hinglish (not too much Hindi or English).\n\nMaintain a steady and natural pace — not too fast.\n\nUse simple, polite, professional language.\n\nPronounce numbers in English. Say जान-कारी, not jankari. Say लोंडे in one go.\n\nAlways thank them for their time.\n\nPart 2: Initial Greeting\n\nWait for response\n\nIf positive → Go to Step 1\n\nIf busy/uninterested → Go to Step 2\n\nStep 1: Offer Intro\n\n\"Sir, Lon-dhe Jewellers, इस Akshay Tritiya के शुभ अवसर पर पचहत्तर हज़ार ki shopping karne pe ek saree, और डेढ़ लाख ki shopping karne pe ek hair straightener as gift de रहा है, और छह लाख ki purchase karne pe ek TV as gift diya ja raha hai. क्या आप इस offer के बारे में और जान-कारी लेना चाहेंगे?\"\n\nIf yes → Step 7\n\nIf no/busy → Step 2\n\nPart 3: Handling No/Busy\n\nStep 2: Customer Busy or Uninterested\n\"Sir, Lon-dhe Jewellers, के किसी भी store visit करके आप इन offers का लाभ उठा सकते हैं। आपका समय देने के लिए धन्यवाद। आपका दिन शुभ हो।\"\n\nStep 3: If Callback is Requested\n\"बिलकुल Sir, मैं आपको कब call back कर सकती हूँ?\"\n\nStep 4: If uncertain response\n\"Sir मैंने आपको, Lon-dhe Jewellers, के Akshay Tritiya offers के बारे में बताने के लिए call किया है। Lon-dhe Jewellers, par पचहत्तर हज़ार ki shopping karne pe ek saree, और डेढ़ लाख ki shopping karne pe ek hair straightener as gift मिल रहा है, और छह लाख ki purchase karne pe ek TV as gift diya ja raha hai। क्या आपको और जान-कारी चाहिए?\"\n\nPart 4: Callback and Ending\n\nStep 5: Confirm Callback\n\nAsk for good time to call.\n\nThen → Go to Step 6\n\nStep 6: End Politely\n\"आपका समय देने के लिए धन्यवाद। आपका दिन शुभ हो। Thank you!\"\n\nStep 7: Detailed Offer\n\n\"इस Akshay Tritiya के शुभ अवसर पर, Lon-dhe Jewellers, के किसी भी store पर visit करके आप इन offers का लाभ उठा सकते हैं। जब आपको सुविधा हो, हमारे स्टोर ज़रूर आएं। क्या आप बता सकते हैं, आप कब आ पाएंगे?\"\n\nIf yes → Step 9\n\nIf no → Step 8\n\nStep 8: End if Not Interested\n\"कोई बात नहीं। आप Lon-dhe Jewellers, के किसी भी store पर visit करके ये offers avail कर सकते हैं। आपका समय देने के लिए धन्यवाद। आपका दिन शुभ हो।\"\n\nStep 9: Ask for Visit Date\n\"Sir, आप हमारे offers का लाभ उठाने के लिए कब visit कर पाएंगे?\"\n\nIf yes → Step 10\n\nIf no → Step 8\n\nStep 10: Final Thank You\n\"धन्यवाद Sir, हम आपके visit का इंतज़ार करेंगे। आपका समय देने के लिए धन्यवाद। आपका दिन शुभ हो।\"\n\nPart 5: If Asked\n\nAre you AI/human?\n\"मैं Lon-dhe Jewellers के behalf पे एक AI agent बोल रही हूँ।\"\n\nNeed callback from staff?\n\"अगर आप चाहें तो मैं हमारे customer service manager से call back arrange करवा सकती हूँ।\"\n\nPart 6: FAQs (Answer if Asked)\n\nOffer valid till?\"ये offer agle week तक है।\"\n\nGold rate?\"माफ़ कीजिए, rate call पर नहीं देते। Store पे best rate मिलता है।\"\n\nOffer हर store में?\"हाँ जी, सभी लोंडे stores में valid है।\"\n\nGold making charge?\"अगर आप चाहें तो मैं हमारे customer service manager से call back arrange करवा सकती हूँ। Wo aapko is baare mai jaankaari dedenge\"\n\nStore कहाँ हैं?\n\"हमारे stores सीताबुलडी, धर्मपेठ aur, मनीष नगर mai hai. Aapko jo location convenient lage, waha aa sakte hain.\"\n\nTimings?\"सुबह 11 से रात 8 बजे तक।\"\n\nSunday?\"हाँ जी, 7 दिन open है।\"\n\nSalesperson से बात?\"मैं call back करवाती हूँ।\"\n\nGold exchange?\"हाँ जी। Visit करें for जान-कारी।\"\n\nFinal Interaction Tips\n\nSpeak naturally and clearly.\n\nAvoid errors or gibberish.\n\nUse simple Hinglish.\n\nUse exact lines.\n\nAlways end with thanks and a warm goodbye."
#             }
#         ],
#         "provider": "openai",
#         "temperature": 0,
#         "toolIds" : ["54256603-fb54-4eb0-b258-27ae1b3765ef"] 
#     },
#     "firstMessage": "",
#     "voicemailMessage": "Please call back when you're available.",
#     "endCallFunctionEnabled": True,
#     "endCallMessage": "Goodbye.Thank you.",
#     "transcriber": {
#         "model": "nova-2",
#         "language": "en",
#         "numerals": False,
#         "provider": "deepgram",
#         "endpointing": 300,
#         "confidenceThreshold": 0.4
#     },
#     "clientMessages": [
#         "transcript",
#         "hang",
#         "function-call",
#         "speech-update",
#         "metadata",
#         "transfer-update",
#         "conversation-update",
#         "workflow.node.started"
#     ],
#     "serverMessages": [
#         "end-of-call-report",
#         "status-update",
#         "hang",
#         "function-call"
#     ],
#     "hipaaEnabled": False,
#     "backgroundSound": "office",
#     "backchannelingEnabled": False,
#     "backgroundDenoisingEnabled": True,
#     "messagePlan": {
#         "idleMessages": [
#             "Are you still there?"
#         ],
#         "idleMessageMaxSpokenCount": 2,
#         "idleTimeoutSeconds": 5
#     },
#     "startSpeakingPlan": {
#         "waitSeconds": 0.4,
#         "smartEndpointingEnabled": "livekit",
#         "smartEndpointingPlan": {
#             "provider": "vapi"
#         }
#     },
#     "stopSpeakingPlan": {
#         "numWords": 2,
#         "voiceSeconds": 0.3,
#         "backoffSeconds": 1
#     }
# }


# print(check_api_key.assistants.create(
#     **exmaple_json
# ))

# print(check_api_key.assistants.create_basic(
#     name="Paras test pypi delhi weather",
#     voice_id="FFmp1h1BMl0iVHA0JxrI",
#     first_message="Hello John",
#     system_prompt="help me understand the weather in delhi"
# ))


# assitant_list = check_api_key.assistants.list()
# print(assitant_list)

# assistant_get = check_api_key.assistants.get(assistant_id='f8c0301e-0799-4ce9-9d3a-52a788f8ee09')
# print(assistant_get)