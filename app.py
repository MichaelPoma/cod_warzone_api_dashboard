from helperFunctions import *

platform = ''
gamertag = ''

app = Flask(__name__)
@app.route("/", methods=['GET','POST'])
def index():

	# Check for platform and gamertag submissions
	if len(request.args.getlist('platform')) == 0 or len(request.args.getlist('gamertag')) == 0:
		return render_template('index.html')
	else:
		# Handle entried data
		platform = request.args.getlist('platform')[0]
		gamertag = request.args.getlist('gamertag')[0]
		gamertag = handleGamertag(gamertag)

		# API CALL 1: load data, and data validation, 20 games

		try:
			df_20games_summary, df_20games_detailed = getData20Games(platform, gamertag)
			print('\nLOADED: 20 games data.\n')
		except:
			# send error back to webpage to display and prompt user to try again
			print('\nFAIL: 20 games data.\n')
			time.sleep(5) # if fails, wait 5 secs
			return render_template('index.html', error='error')

		# API CALL 2: load data, and data validation, lifetime
		try:
			df_lifetime, temp = getDataLifetime(platform, gamertag)
			print('\nLOADED: Lifetime data.\n')
		except:
			# send error back to webpage to display and prompt user to try again
			print('\nFAIL: Lifetime data.\n')
			time.sleep(5) # if fails, wait 5 secs
			return render_template('index.html', error='error')

		# API CALL 3: load data, and data validation, weekly	
		try:
			df_weekly, temp = getDataWeekly(platform, gamertag)
			print('\nLOADED: Weekly data.\n')
		except:
			# send error back to webpage to display and prompt user to try again
			print('\nFAIL: Weekly data.\n')
			time.sleep(5) # if fails, wait 5 secs
			return render_template('index.html', error='error')


		# all data loaded successfully:
		# convert gamertag back to normal
		gamertag_normal = convertGamertagBack(gamertag)

		return render_template('index.html',
								success='success',
								gamertag=gamertag_normal,
								data_lifetime=list(df_lifetime.values.tolist()),
								data_weekly=list(df_weekly.values.tolist()),
								data_detailed=json.dumps(json.loads(df_20games_detailed.to_json(orient="columns")), indent=4))

if __name__ == "__main__":
	app.run()

