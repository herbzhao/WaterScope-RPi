steps_plan = []
# first move coarsly
steps_plan += [250]*6
steps_plan += [-6*250]
steps_plan += [-250]*6
steps_plan.append('phase 1 complete')

# finer plan
steps_plan += [100]*5
steps_plan += [-5*100]
steps_plan += [-100]*5
steps_plan += 'phase 2 complete'

# finest plan
steps_plan += [25]*5
steps_plan += [-5*25]
steps_plan += [-25]
steps_plan += 'phase 3 complete'


print(steps_plan)