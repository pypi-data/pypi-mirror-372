# create the database
canYouDigIt init --truerun
# create the jobs
canYouDigIt jobs create --truerun
# list the jobs (if you want to see what was created)
canYouDigIt jobs info
# create the runs
canYouDigIt runs create --run_name "test" --truerun
# list the runs (if you want to see what was created)
canYouDigIt runs infio
# execute locally the runs (in sequential)
canYouDigIt runs launch --truerun
# you can control that the jobs ran
canYouDigIt runs info
# you see the details of a run
canYouDigIt runs info --run_id 1# create the database
canYouDigIt init --truerun
# create the jobs
canYouDigIt jobs create --truerun
# list the jobs (if you want to see what was created)
canYouDigIt jobs info
# create the runs
canYouDigIt runs create --run_name "test" --truerun
# list the runs (if you want to see what was created)
canYouDigIt runs infio
# execute locally the runs (in sequential)
canYouDigIt runs launch --truerun
# you can control that the jobs ran
canYouDigIt runs info
# you see the details of a run
canYouDigIt runs info --run_id 1
