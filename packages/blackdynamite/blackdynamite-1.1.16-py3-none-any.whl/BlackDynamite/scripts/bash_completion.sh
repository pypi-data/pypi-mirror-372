which register-python-argcomplete > /dev/null
if [ $? = 0 ]; then
    eval "$(register-python-argcomplete canYouDigIt.py)"
    eval "$(register-python-argcomplete cleanRuns.py)"
    eval "$(register-python-argcomplete createDB.py)"
    eval "$(register-python-argcomplete createJobs.py)"
    eval "$(register-python-argcomplete createRuns.py)"
    eval "$(register-python-argcomplete getRunInfo.py)"
    eval "$(register-python-argcomplete launchRuns.py)"
    eval "$(register-python-argcomplete pushQuantity.py)"
    eval "$(register-python-argcomplete updateRuns.py)"
fi