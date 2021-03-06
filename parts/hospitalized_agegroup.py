from parts.amortizedmarkov import ProbState


class AgeGroup:
	def __init__(self, subgroupstats, name=None):

		self.name = name
		self.stats = subgroupstats
		# Variables to store state changes

		# Probability states
		if self.name is not None:
			self.isolated = ProbState(14,  name=f"{self.name}: isolated")
		else:
			self.isolated = ProbState(14)
		self.h_noncrit  = ProbState(8)
		self.h_post_icu = ProbState(6)
		self.h_icu      = ProbState(10)
		self.h_icu_vent = ProbState(10)
		self.recovered  = ProbState(1000)
		self.deceased   = ProbState(1000)

		self.isolated.add_exit_state(self.recovered, 1)
		self.isolated.normalize_states_over_period()

		self.h_noncrit.add_exit_state(self.recovered, 1)
		self.h_noncrit.normalize_states_over_period()

		self.h_icu.add_exit_state(self.deceased,   self.stats.p_icu_death)
		self.h_icu.add_exit_state(self.h_post_icu, self.stats.p_icu_recovery)
		self.h_icu.normalize_states_over_period()

		self.h_icu_vent.add_exit_state(self.deceased,   self.stats.p_icu_death)
		self.h_icu_vent.add_exit_state(self.h_post_icu, self.stats.p_icu_recovery)
		self.h_icu_vent.normalize_states_over_period()

		self.h_post_icu.add_exit_state(self.recovered, 1)
		self.h_post_icu.normalize_states_over_period()


	# Add N people to the list of infected
	def apply_infections(self, infections):
		inf_float = float(infections)
		self.isolated.store_pending(inf_float * self.stats.p_selfisolate)
		self.h_noncrit.store_pending(inf_float * self.stats.p_nevercrit)
		self.h_icu.store_pending(inf_float * self.stats.p_icu_nonvent)
		self.h_icu_vent.store_pending(inf_float * self.stats.p_icu_vent)

	def calculate_redistributions(self):
		self.isolated.pass_downstream()
		self.h_noncrit.pass_downstream()
		self.h_icu.pass_downstream()
		self.h_icu_vent.pass_downstream()

	def apply_pending(self):
		self.isolated.apply_pending()
		self.h_noncrit.apply_pending()
		self.h_icu.apply_pending()
		self.h_icu_vent.apply_pending()
		self.recovered.apply_pending()
		self.deceased.apply_pending()
