# https://globaltriviaroom.com/

Please note for project part 3 obj 1 a sense of time, there is one feature "Timing must be initiated by a user[s]". It is no immediately obvious but our app accomplishes this by pausing the game loop while there are no users. You will notice that if there are no users the “last message” line will display the fact that the current question is the first question in the game loop.


Project Part 3 Objective 3:
The unique feature for this app is to take advantage of API calls to populate the game’s questions and answers. Calls are made to https://opentdb.com/api.php?amount=1&type=multiple. No other objective required the use of calls for an outside api over the web. 
Testing Procedure
1.	Navigate to consumers.py and scroll down to the trivia_api() function and confirm that it makes an api call.
2.	Navigate to the app, register a user, log in, and head to the game screen. Confirm that the trivia question shows correctly. Wait for a minute and confirm that the trivia questions update every 10 seconds (Please note, duplicate questions can appear. Even if a duplicate question appears, the “last answer was” line should correctly update).
3.	Confirm that the “last answer was” line shows the correct answer for the last question (This will also test your trivia skill).
