# MovieBot
natural language requests for Magic Tiger

<<in progress>>

idea of an 'expert system' with a knowledge base and logical rule-set.
keeps track of state and can respond to certain movie-related inputs

knowledge takes care of scraping and parsing information from the internet/stored files

tokeniser parses information from the customer, looking for cues like numbers, names of movies
and theaters, and times

logic takes tokenised information and attempts to fill in the request object, making
sure that the information is mutually compatible


to play with:
run Bot file with interpreter
bot = Bot()
bot.run()
interact with bot on the console
will finish by either fulfilling a request, or if you input "bye"
