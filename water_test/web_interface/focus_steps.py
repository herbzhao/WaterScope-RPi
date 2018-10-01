coarse_steps_plan = []
# first move up to the end stop and go back to centre
# TODO: read the plan's led_off and on to turn on and off
coarse_steps_plan.append('led_off')
coarse_steps_plan += [-8000, 4000]
coarse_steps_plan.append('led_on')

# first plan: 2000
coarse_steps_plan += [0]
coarse_steps_plan += [500]*4
coarse_steps_plan += [-4*500]
coarse_steps_plan += [-500]*4
coarse_steps_plan.append('phase 1 complete')


# first plan: 2000
coarse_steps_plan += [200]*3
coarse_steps_plan += [-3*200]
coarse_steps_plan += [-200]*3
coarse_steps_plan.append('phase 1 complete')

# finer plan : 800
coarse_steps_plan += [100]*3
coarse_steps_plan += [-3*100]
coarse_steps_plan += [-100]*3
coarse_steps_plan.append('phase 2 complete')

# finest plan: 400
coarse_steps_plan += [50]*3
coarse_steps_plan += [-3*50]
coarse_steps_plan += [-50]*3
coarse_steps_plan.append('phase 3 complete')


# finest plan: 200
coarse_steps_plan += [25]*3
coarse_steps_plan += [-3*25]
coarse_steps_plan += [-25]*3
coarse_steps_plan.append('phase 4 complete')
coarse_steps_plan.append('auto-focusing complete')




fine_steps_plan = []

# finer plan : 800
fine_steps_plan += [100]*3
fine_steps_plan += [-3*100]
fine_steps_plan += [-100]*3
fine_steps_plan.append('phase 1 complete')

# finest plan: 400
fine_steps_plan += [50]*3
fine_steps_plan += [-3*50]
fine_steps_plan += [-50]*3
fine_steps_plan.append('phase 2 complete')


# finest plan: 200
fine_steps_plan += [25]*3
fine_steps_plan += [-3*25]
fine_steps_plan += [-25]*3
fine_steps_plan.append('phase 3 complete')
fine_steps_plan.append('auto-focusing complete')