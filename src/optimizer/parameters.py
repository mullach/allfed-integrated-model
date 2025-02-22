"""
############################### Parameters ####################################
##                                                                            #
##           Calculates all the parameters that feed into the optimizer       #
##                                                                            #
###############################################################################
"""
# TODO: make a couple sub functions that deal with the different parts, where
#      it assigns the returned values to the constants.
import numpy as np
from src.food_system.meat_and_dairy import MeatAndDairy
from src.food_system.outdoor_crops import OutdoorCrops
from src.food_system.seafood import Seafood
from src.food_system.stored_food import StoredFood
from src.food_system.cellulosic_sugar import CellulosicSugar
from src.food_system.greenhouses import Greenhouses
from src.food_system.methane_scp import MethaneSCP
from src.food_system.seaweed import Seaweed
from src.food_system.feed_and_biofuels import FeedAndBiofuels
from src.food_system.food import Food
from src.food_system.calculate_animals_and_feed_over_time import CalculateAnimalOutputs


class Parameters:
    def __init__(self):
        self.FIRST_TIME_RUN = True
        self.SIMULATION_STARTING_MONTH = "MAY"
        # Dictionary of the months to set the starting point of the model to
        # the months specified in parameters.py
        months_dict = {
            "JAN": 1,
            "FEB": 2,
            "MAR": 3,
            "APR": 4,
            "MAY": 5,
            "JUN": 6,
            "JUL": 7,
            "AUG": 8,
            "SEP": 9,
            "OCT": 10,
            "NOV": 11,
            "DEC": 12,
        }
        self.SIMULATION_STARTING_MONTH_NUM = months_dict[self.SIMULATION_STARTING_MONTH]

    def compute_parameters(self, constants_inputs, scenarios_loader):
        # TODO: is this still necessary?
        if (
            constants_inputs["DELAY"]["FEED_SHUTOFF_MONTHS"] > 0
            or constants_inputs["DELAY"]["BIOFUEL_SHUTOFF_MONTHS"] > 0
        ):
            assert (
                constants_inputs["ADD_MAINTAINED_MEAT"] is True
            ), "Maintained meat needs to be added for continued feed usage"
        assert self.FIRST_TIME_RUN
        self.FIRST_TIME_RUN = False

        PRINT_SCENARIO_PROPERTIES = True
        if PRINT_SCENARIO_PROPERTIES:
            print(scenarios_loader.scenario_description)

        # ensure every parameter has been initialized for the scenarios_loader
        scenarios_loader.check_all_set()

        # time dependent constants_out as inputs to the optimizer
        time_consts = {}
        constants_out = {}

        print("")
        print("")
        print("")
        constants_out = self.init_scenario(constants_out, constants_inputs)

        # NUTRITION PER MONTH #

        constants_out = self.set_nutrition_per_month(constants_out, constants_inputs)

        # SEAWEED INITIAL VARIABLES #

        constants_out, built_area, growth_rates, seaweed = self.set_seaweed_params(
            constants_out, constants_inputs
        )

        time_consts["built_area"] = built_area
        time_consts["growth_rates_monthly"] = growth_rates

        # FISH #
        time_consts, constants_out = self.init_fish_params(
            constants_out, time_consts, constants_inputs
        )

        # CONSTANTS FOR METHANE SINGLE CELL PROTEIN #
        time_consts, methane_scp = self.init_scp_params(time_consts, constants_inputs)

        # CONSTANTS FOR CELLULOSIC SUGAR #
        time_consts, cellulosic_sugar = self.init_cs_params(
            time_consts, constants_inputs
        )

        # CROP PRODUCTION VARIABLES #

        constants_out, outdoor_crops = self.init_outdoor_crops(
            constants_out, constants_inputs
        )

        # CONSTANTS FOR GREENHOUSES #

        time_consts = self.init_greenhouse_params(
            time_consts, constants_inputs, outdoor_crops
        )

        # STORED FOOD VARIABLES #

        constants_out, stored_food = self.init_stored_food(
            constants_out, constants_inputs, outdoor_crops
        )

        (
            constants_out,
            time_consts,
            feed_and_biofuels,
        ) = self.init_meat_and_dairy_and_feed_from_breeding_and_subtract_feed_biofuels(
            constants_out,
            constants_inputs,
            time_consts,
            outdoor_crops,
            methane_scp,
            cellulosic_sugar,
            seaweed,
            stored_food,
        )

        # else:
        # # FEED AND BIOFUEL VARIABLES #

        # OTHER VARIABLES #
        constants_out["inputs"] = constants_inputs

        return (constants_out, time_consts, feed_and_biofuels)

    def assert_constants_not_nan(self, single_valued_constants, time_consts):
        """
        this is a utility function to
        make sure there's nothing fishy going on with the constants (no nan's)
        (otherwise the linear optimizer will fail in a very mysterious way)
        """

        # assert dictionary single_valued_constants values are all not nan
        for k, v in single_valued_constants.items():
            self.assert_dictionary_value_not_nan(k, v)

        for month_key, month_value in time_consts.items():
            for v in month_value:
                self.assert_dictionary_value_not_nan(month_key, v)

    def assert_dictionary_value_not_nan(self, key, value):
        """
        assert if a dictionary value is not nan.  if it is, assert, and print the key.
        """

        if key == "inputs":
            # inputs to the parameters -- not going to check these are nan here.
            # but, they might be the culprit!
            return

        # all non-integers should be Food types, and must have the following function
        if (
            isinstance(value, int)
            or isinstance(value, float)
            or isinstance(value, bool)
        ):
            assert not (value != value), "dictionary has nan at key" + key
            return

        value.make_sure_not_nan()

    def init_scenario(self, constants_out, constants_inputs):
        """
        Initialize the scenario for some constants_out used for the optimizer.
        """

        # population
        self.POP = constants_inputs["POP"]
        # population in units of millions of people
        self.POP_BILLIONS = constants_inputs["POP"] / 1e9
        constants_out = {}
        constants_out["POP"] = self.POP
        constants_out["POP_BILLIONS"] = self.POP_BILLIONS

        # full months duration of simulation

        # single valued inputs to optimizer
        constants_out["NMONTHS"] = constants_inputs["NMONTHS"]
        constants_out["ADD_FISH"] = constants_inputs["ADD_FISH"]
        constants_out["ADD_SEAWEED"] = constants_inputs["ADD_SEAWEED"]
        constants_out["ADD_MAINTAINED_MEAT"] = constants_inputs["ADD_MAINTAINED_MEAT"]
        constants_out["ADD_CULLED_MEAT"] = constants_inputs["ADD_CULLED_MEAT"]
        constants_out["ADD_MILK"] = constants_inputs["ADD_MILK"]
        constants_out["ADD_STORED_FOOD"] = constants_inputs["ADD_STORED_FOOD"]
        constants_out["ADD_METHANE_SCP"] = constants_inputs["ADD_METHANE_SCP"]
        constants_out["ADD_CELLULOSIC_SUGAR"] = constants_inputs["ADD_CELLULOSIC_SUGAR"]
        constants_out["ADD_GREENHOUSES"] = constants_inputs["ADD_GREENHOUSES"]
        constants_out["ADD_OUTDOOR_GROWING"] = constants_inputs["ADD_OUTDOOR_GROWING"]
        constants_out["STORE_FOOD_BETWEEN_YEARS"] = constants_inputs[
            "STORE_FOOD_BETWEEN_YEARS"
        ]

        return constants_out

    def set_nutrition_per_month(self, constants_out, constants_inputs):
        """
        Set the nutrition per month for the simulation.
        """

        # we will assume a 2100 kcals diet, and scale the "upper safe" nutrition
        # from the spreadsheet down to this "standard" level.
        # we also add 20% loss, according to the sorts of loss seen in this spreadsheet
        KCALS_DAILY = constants_inputs["NUTRITION"]["KCALS_DAILY"]
        FAT_DAILY = constants_inputs["NUTRITION"]["FAT_DAILY"]
        PROTEIN_DAILY = constants_inputs["NUTRITION"]["PROTEIN_DAILY"]
        constants_out["KCALS_DAILY"] = KCALS_DAILY
        constants_out["FAT_DAILY"] = FAT_DAILY
        constants_out["PROTEIN_DAILY"] = PROTEIN_DAILY

        Food.conversions.set_nutrition_requirements(
            kcals_daily=KCALS_DAILY,
            fat_daily=FAT_DAILY,
            protein_daily=PROTEIN_DAILY,
            include_fat=constants_inputs["INCLUDE_FAT"],
            include_protein=constants_inputs["INCLUDE_PROTEIN"],
            population=self.POP,
        )

        constants_out["BILLION_KCALS_NEEDED"] = Food.conversions.billion_kcals_needed
        constants_out["THOU_TONS_FAT_NEEDED"] = Food.conversions.thou_tons_fat_needed
        constants_out[
            "THOU_TONS_PROTEIN_NEEDED"
        ] = Food.conversions.thou_tons_protein_needed

        constants_out["KCALS_MONTHLY"] = Food.conversions.kcals_monthly
        constants_out["PROTEIN_MONTHLY"] = Food.conversions.protein_monthly
        constants_out["FAT_MONTHLY"] = Food.conversions.fat_monthly

        CONVERSION_TO_KCALS = self.POP / 1e9 / KCALS_DAILY
        CONVERSION_TO_FAT = self.POP / 1e9 / FAT_DAILY
        CONVERSION_TO_PROTEIN = self.POP / 1e9 / PROTEIN_DAILY

        constants_out["CONVERSION_TO_KCALS"] = CONVERSION_TO_KCALS
        constants_out["CONVERSION_TO_FAT"] = CONVERSION_TO_FAT
        constants_out["CONVERSION_TO_PROTEIN"] = CONVERSION_TO_PROTEIN

        return constants_out

    def set_seaweed_params(self, constants_out, constants_inputs):
        """
        Set the seaweed parameters.
        """
        seaweed = Seaweed(constants_inputs)

        # determine area built to enable seaweed to grow there
        built_area = seaweed.get_built_area(constants_inputs)

        # determine growth rates
        growth_rates = seaweed.get_growth_rates(constants_inputs)

        constants_out["INITIAL_SEAWEED"] = seaweed.INITIAL_SEAWEED
        constants_out["SEAWEED_KCALS"] = seaweed.SEAWEED_KCALS
        constants_out["HARVEST_LOSS"] = seaweed.HARVEST_LOSS
        constants_out["SEAWEED_FAT"] = seaweed.SEAWEED_FAT
        constants_out["SEAWEED_PROTEIN"] = seaweed.SEAWEED_PROTEIN

        constants_out["MINIMUM_DENSITY"] = seaweed.MINIMUM_DENSITY
        constants_out["MAXIMUM_DENSITY"] = seaweed.MAXIMUM_DENSITY
        constants_out["MAXIMUM_SEAWEED_AREA"] = seaweed.MAXIMUM_SEAWEED_AREA
        constants_out["INITIAL_BUILT_SEAWEED_AREA"] = seaweed.INITIAL_BUILT_SEAWEED_AREA
        constants_out[
            "MAX_SEAWEED_HUMANS_CAN_CONSUME_MONTHLY"
        ] = seaweed.MAX_SEAWEED_HUMANS_CAN_CONSUME_MONTHLY

        return constants_out, built_area, growth_rates, seaweed

    def init_outdoor_crops(self, constants_out, constants_inputs):
        """
        initialize the outdoor crops parameters
        """
        constants_inputs["STARTING_MONTH_NUM"] = self.SIMULATION_STARTING_MONTH_NUM

        outdoor_crops = OutdoorCrops(constants_inputs)
        outdoor_crops.calculate_rotation_ratios(constants_inputs)
        outdoor_crops.calculate_monthly_production(constants_inputs)

        constants_out["OG_FRACTION_FAT"] = outdoor_crops.OG_FRACTION_FAT
        constants_out["OG_FRACTION_PROTEIN"] = outdoor_crops.OG_FRACTION_PROTEIN

        constants_out[
            "OG_ROTATION_FRACTION_KCALS"
        ] = outdoor_crops.OG_ROTATION_FRACTION_KCALS
        constants_out[
            "OG_ROTATION_FRACTION_FAT"
        ] = outdoor_crops.OG_ROTATION_FRACTION_FAT
        constants_out[
            "OG_ROTATION_FRACTION_PROTEIN"
        ] = outdoor_crops.OG_ROTATION_FRACTION_PROTEIN

        return constants_out, outdoor_crops

    def init_stored_food(self, constants_out, constants_inputs, outdoor_crops):
        stored_food = StoredFood(constants_inputs, outdoor_crops)
        if constants_out["ADD_STORED_FOOD"]:
            stored_food.calculate_stored_food_to_use(self.SIMULATION_STARTING_MONTH_NUM)
        else:
            stored_food.initial_available = Food(
                kcals=np.zeros(constants_inputs["NMONTHS"]),
                fat=np.zeros(constants_inputs["NMONTHS"]),
                protein=np.zeros(constants_inputs["NMONTHS"]),
                kcals_units="billion kcals each month",
                fat_units="thousand tons each month",
                protein_units="thousand tons each month",
            )

        constants_out["SF_FRACTION_FAT"] = stored_food.SF_FRACTION_FAT
        constants_out["SF_FRACTION_PROTEIN"] = stored_food.SF_FRACTION_PROTEIN
        constants_out["stored_food"] = stored_food

        return constants_out, stored_food

    def init_fish_params(self, constants_out, time_consts, constants_inputs):
        """
        Initialize seafood parameters, not including seaweed
        """
        seafood = Seafood(constants_inputs)

        (
            production_kcals_fish_per_month,
            production_fat_fish_per_month,
            production_protein_fish_per_month,
        ) = seafood.get_seafood_production(constants_inputs)

        time_consts["production_kcals_fish_per_month"] = production_kcals_fish_per_month
        time_consts[
            "production_protein_fish_per_month"
        ] = production_protein_fish_per_month
        time_consts["production_fat_fish_per_month"] = production_fat_fish_per_month

        constants_out["FISH_KCALS"] = seafood.FISH_KCALS
        constants_out["FISH_FAT"] = seafood.FISH_FAT
        constants_out["FISH_PROTEIN"] = seafood.FISH_PROTEIN

        return time_consts, constants_out

    def init_greenhouse_params(self, time_consts, constants_inputs, outdoor_crops):
        """
        Initialize the greenhouse parameters.
        """
        greenhouses = Greenhouses(constants_inputs)

        greenhouse_area = greenhouses.get_greenhouse_area(
            constants_inputs, outdoor_crops
        )
        time_consts["greenhouse_area"] = greenhouse_area

        if constants_inputs["INITIAL_CROP_AREA_FRACTION"] == 0:
            greenhouse_kcals_per_ha = np.zeros(constants_inputs["NMONTHS"])
            greenhouse_fat_per_ha = np.zeros(constants_inputs["NMONTHS"])
            greenhouse_protein_per_ha = np.zeros(constants_inputs["NMONTHS"])
        else:
            (
                greenhouse_kcals_per_ha,
                greenhouse_fat_per_ha,
                greenhouse_protein_per_ha,
            ) = greenhouses.get_greenhouse_yield_per_ha(constants_inputs, outdoor_crops)
        # post-waste crops food produced
        outdoor_crops.set_crop_production_minus_greenhouse_area(
            constants_inputs, greenhouses.greenhouse_fraction_area
        )
        time_consts["outdoor_crops"] = outdoor_crops
        time_consts["greenhouse_kcals_per_ha"] = greenhouse_kcals_per_ha
        time_consts["greenhouse_fat_per_ha"] = greenhouse_fat_per_ha
        time_consts["greenhouse_protein_per_ha"] = greenhouse_protein_per_ha

        return time_consts

    def init_cs_params(self, time_consts, constants_inputs):
        """
        Initialize the parameters for the cellulosic sugar model
        """

        cellulosic_sugar = CellulosicSugar(constants_inputs)
        cellulosic_sugar.calculate_monthly_cs_production(constants_inputs)

        time_consts["cellulosic_sugar"] = cellulosic_sugar

        return time_consts, cellulosic_sugar

    def init_scp_params(self, time_consts, constants_inputs):
        """
        Initialize the parameters for single cell protein
        """

        methane_scp = MethaneSCP(constants_inputs)
        methane_scp.calculate_monthly_scp_caloric_production(constants_inputs)
        methane_scp.calculate_scp_fat_and_protein_production()

        time_consts["methane_scp"] = methane_scp

        return time_consts, methane_scp

    def init_meat_and_dairy_and_feed_from_breeding_and_subtract_feed_biofuels(
        self,
        constants_out,
        constants_inputs,
        time_consts,
        outdoor_crops,
        methane_scp,
        cellulosic_sugar,
        seaweed,
        stored_food,
    ):
        """
        In the case of a breeding reduction strategy rather than increased slaughter,
        we first calculate the expected amount of livestock if breeding were quickly
        reduced and slaughter only increased slightly, then using that we calculate the
        feed they would use given the expected input animal populations over time.
        """
        feed_and_biofuels = FeedAndBiofuels(constants_inputs)
        meat_and_dairy = MeatAndDairy(constants_inputs)

        # TODO: parametrize these constants in the scenarios so they can be adjusted
        # without messing with the code

        # This function encodes the fact that the use of improved crop rotations ALSO alters the
        # way we treat dairy cattle
        # In particular, if we are using improved crop rotations, part of this is assuming dairy cattle
        # are fully fed by grass
        # If we aren't using improved rotations (a somewhat more pessimistic outcome), we stop breeding
        # cattle entirely and don't use up any of the grass
        # for dairy output.
        if constants_inputs["OG_USE_BETTER_ROTATION"]:
            reduction_in_dairy_calves = 0
            use_grass_and_residues_for_dairy = True
        else:
            reduction_in_dairy_calves = 100
            use_grass_and_residues_for_dairy = False

        cao = CalculateAnimalOutputs()

        # if we have an immediate shutoff, then turn off the feed to animals entirely
        if constants_inputs["DELAY"]["FEED_SHUTOFF_MONTHS"] == 0:
            feed_ratio = 0
        else:
            feed_ratio = 1

        (
            biofuels_before_cap_prewaste,
            feed_before_cap_prewaste,
            meat_and_dairy,
            time_consts,
            constants_out,
        ) = self.init_meat_and_dairy_and_feed_from_breeding(
            constants_inputs,
            reduction_in_dairy_calves,
            use_grass_and_residues_for_dairy,
            cao,
            feed_and_biofuels,
            meat_and_dairy,
            feed_ratio,
            constants_out,
            time_consts,
        )

        # # this only works for countries that will have enough to provide for combined feed for all the animals.
        # combined_nonhuman_consumption_before_cap_or_waste = (
        #     biofuels_before_cap_prewaste + feed_before_cap_prewaste
        # )

        (
            time_consts,
            constants_out,
            feed_and_biofuels,
        ) = self.subtract_feed_and_biofuels_from_production(
            constants_inputs,
            time_consts,
            constants_out,
            biofuels_before_cap_prewaste,
            feed_before_cap_prewaste,
            seaweed,
            cellulosic_sugar,
            methane_scp,
            outdoor_crops,
            stored_food,
            feed_and_biofuels,
        )

        # # make sure nonhuman consumption is always less than or equal
        # # to outdoor crops+stored food for all nutrients, PRE-WASTE
        # # in the case that feed usage is impossibly high, and it's reduced, meat is reduced as well
        # # This results in a new value assigned to "culled_meat" (note: "maintained_meat" is an artifact of the
        # # old way of calculating meat production)
        # ratio = feed_and_biofuels.set_nonhuman_consumption_with_cap(
        #     constants_inputs,
        #     outdoor_crops,  # net_feed_available_without_stored_food,
        #     stored_food,
        #     biofuels_before_cap_prewaste,
        #     feed_before_cap_prewaste,
        #     excess_feed_prewaste,
        # )

        # if ratio < 1:
        #     # impossibly high feed demands, we reduced feed, now we have to reduce meat ouput accordingly
        #     (
        #         biofuels_before_cap_prewaste,
        #         feed_before_cap_prewaste,
        #         excess_feed_prewaste,
        #         feed_and_biofuels,
        #         meat_and_dairy,
        #         time_consts,
        #         constants_out,
        #     ) = self.init_meat_and_dairy_and_feed_from_breeding(
        #         constants_inputs,
        #         reduction_in_dairy_calves,
        #         use_grass_and_residues_for_dairy,
        #         cao,
        #         feed_and_biofuels,
        #         meat_and_dairy,
        #         ratio,
        #         constants_out,
        #         time_consts,
        #     )

        # feed_and_biofuels.nonhuman_consumption = (
        #     feed_and_biofuels.biofuels + feed_and_biofuels.feed
        # )

        # nonhuman_consumption = feed_and_biofuels.nonhuman_consumption

        # post waste
        # time_consts["nonhuman_consumption"] = nonhuman_consumption
        # time_consts[
        #     "excess_feed"
        # ] = feed_and_biofuels.get_excess_food_usage_from_percents(
        #     constants_inputs["EXCESS_FEED_PERCENT"]
        # )
        # return feed_and_biofuels, meat_and_dairy, constants_out, time_consts
        time_consts = self.add_dietary_constraints_to_scp_and_cs(
            constants_out, time_consts
        )
        return (
            constants_out,
            time_consts,
            feed_and_biofuels,
        )

    def add_dietary_constraints_to_scp_and_cs(self, constants_out, time_consts):
        if constants_out["ADD_METHANE_SCP"]:
            # loop through the methane SCP and make sure it's never greater than
            # the minimum fraction able to be eaten by humans.
            # If it is greater, reduce it to the minimum.
            capped_kcals_ratios = np.array([])
            methane_scp = time_consts["methane_scp"]
            methane_scp_fraction = (
                methane_scp.for_humans.in_units_percent_fed().kcals / 100
            )
            capped_kcals_ratios = []
            for month in range(0, len(methane_scp_fraction)):
                capped_kcals_ratios.append(
                    min(
                        methane_scp_fraction[month],
                        methane_scp.MAX_FRACTION_HUMAN_FOOD_CONSUMED_AS_SCP,
                    )
                )
            time_consts["methane_scp"].for_humans = methane_scp.for_humans * np.array(
                capped_kcals_ratios
            )

        if constants_out["ADD_CELLULOSIC_SUGAR"]:
            # loop through the cellulosic sugar and make sure it's never greater than
            # the minimum fraction able to be eaten by humans.
            # If it is greater, reduce it to the minimum.
            capped_kcals_ratios = np.array([])
            cellulosic_sugar = time_consts["cellulosic_sugar"]
            cellulosic_sugar.for_humans.make_sure_is_a_list()
            cellulosic_sugar_fraction = (
                cellulosic_sugar.for_humans.in_units_percent_fed().kcals / 100
            )
            capped_kcals_ratios = []
            for month in range(0, len(cellulosic_sugar_fraction)):
                capped_kcals_ratios.append(
                    min(
                        cellulosic_sugar_fraction[month],
                        cellulosic_sugar.MAX_FRACTION_HUMAN_FOOD_CONSUMED_AS_CS,
                    )
                )

            time_consts[
                "cellulosic_sugar"
            ].for_humans = cellulosic_sugar.for_humans * np.array(capped_kcals_ratios)

        return time_consts

    def subtract_feed_and_biofuels_from_production(
        self,
        constants_inputs,
        time_consts,
        constants_out,
        biofuels_before_cap_prewaste,
        feed_before_cap_prewaste,
        seaweed,
        cellulosic_sugar,
        methane_scp,
        outdoor_crops,
        stored_food,
        feed_and_biofuels,
    ):
        (
            outdoor_crops_remaining_after_biofuel,
            remaining_biofuel_needed_from_stored_food,
            outdoor_crops_used_for_biofuel,
            methane_scp_used_for_biofuel,
            cellulosic_sugar_used_for_biofuel,
        ) = self.calculate_biofuel_components_without_stored_food(
            constants_inputs["INCLUDE_FAT"] or constants_inputs["INCLUDE_PROTEIN"],
            biofuels_before_cap_prewaste,
            seaweed,
            cellulosic_sugar,
            methane_scp,
            outdoor_crops,
        )

        cellulosic_sugar_remaining_after_biofuel = np.subtract(
            cellulosic_sugar.production.kcals,
            cellulosic_sugar_used_for_biofuel,
        )
        methane_scp_remaining_after_biofuel = np.subtract(
            methane_scp.production.kcals,
            methane_scp_used_for_biofuel,
        )
        (
            outdoor_crops_remaining_after_feed_and_biofuel,
            remaining_feed_needed_from_stored_food,
            outdoor_crops_used_for_feed,
            methane_scp_used_for_feed,
            cellulosic_sugar_used_for_feed,
        ) = self.calculate_feed_components_without_stored_food(
            constants_inputs["INCLUDE_FAT"] or constants_inputs["INCLUDE_PROTEIN"],
            feed_before_cap_prewaste,
            cellulosic_sugar.MAX_FRACTION_FEED_CONSUMED_AS_CELLULOSIC_SUGAR,
            methane_scp.MAX_FRACTION_FEED_CONSUMED_AS_SCP,
            cellulosic_sugar_remaining_after_biofuel,
            methane_scp_remaining_after_biofuel,
            outdoor_crops_remaining_after_biofuel,
        )

        feed_and_biofuels.set_feed_and_biofuels(
            outdoor_crops_used_for_biofuel,
            methane_scp_used_for_biofuel,
            cellulosic_sugar_used_for_biofuel,
            remaining_biofuel_needed_from_stored_food,
            outdoor_crops_used_for_feed,
            methane_scp_used_for_feed,
            cellulosic_sugar_used_for_feed,
            remaining_feed_needed_from_stored_food,
        )

        methane_scp_remaining_after_feed_and_biofuel = (
            methane_scp_remaining_after_biofuel - methane_scp_used_for_feed
        )
        cellulosic_sugar_remaining_after_feed_and_biofuel = (
            cellulosic_sugar_remaining_after_biofuel - cellulosic_sugar_used_for_feed
        )

        # TODO: INCLUDE FAT AND PROTEIN HERE RATHER THAN JUST MAKING THEM ZERO!!!
        outdoor_crops.for_humans = Food(
            kcals=outdoor_crops_remaining_after_feed_and_biofuel,
            fat=np.zeros(constants_inputs["NMONTHS"]),
            protein=np.zeros(constants_inputs["NMONTHS"]),
            kcals_units=outdoor_crops.production.kcals_units,
            fat_units=outdoor_crops.production.fat_units,
            protein_units=outdoor_crops.production.protein_units,
        )
        methane_scp.for_humans = Food(
            kcals=methane_scp_remaining_after_feed_and_biofuel,
            fat=np.zeros(constants_inputs["NMONTHS"]),
            protein=np.zeros(constants_inputs["NMONTHS"]),
            kcals_units=methane_scp.production.kcals_units,
            fat_units=methane_scp.production.fat_units,
            protein_units=methane_scp.production.protein_units,
        )
        cellulosic_sugar.for_humans = Food(
            kcals=cellulosic_sugar_remaining_after_feed_and_biofuel,
            fat=np.zeros(constants_inputs["NMONTHS"]),
            protein=np.zeros(constants_inputs["NMONTHS"]),
            kcals_units=cellulosic_sugar.production.kcals_units,
            fat_units=cellulosic_sugar.production.fat_units,
            protein_units=cellulosic_sugar.production.protein_units,
        )

        assert (
            remaining_feed_needed_from_stored_food.all_greater_than_or_equal_to_zero()
        )
        assert (
            remaining_biofuel_needed_from_stored_food.all_greater_than_or_equal_to_zero()
        )
        total_feed_usage_stored_food = (
            remaining_feed_needed_from_stored_food.get_nutrients_sum()
            + remaining_biofuel_needed_from_stored_food.get_nutrients_sum()
        )

        assert total_feed_usage_stored_food.all_greater_than_or_equal_to_zero()
        # assert (
        #     np.max(running_demand_for_stored_food) == running_demand_for_stored_food[-1]
        # )
        # this means that we have enough calories for all the feed.
        # otherwise, we'd need to somehow reduce feed demand.

        # the total demand needed all added up
        stored_food.initial_available_to_humans = (
            stored_food.initial_available - total_feed_usage_stored_food
        )

        if (
            not stored_food.initial_available_to_humans.all_greater_than_or_equal_to_zero()
        ):
            print("")
            print(
                "WARNING: THE INPUT ASSUMPTIONS FOR THE SCENARIO CONSIDERED ARE UNREALISTIC!"
            )
            print(
                "         You have chosen an amount of feed and biofuels which are untenable"
            )
            print(
                "         and cannot be satisfied by the outdoor crop production, available"
            )
            print(
                "         cellulosic sugar, and available methane single cell protein."
            )
            print(
                "         The feed required before waste comes to "
                + str(feed_before_cap_prewaste.get_nutrients_sum()).strip()
                + " over the entire simulation."
            )
            print(
                "         The biofuels required before waste comes to "
                + str(biofuels_before_cap_prewaste.get_nutrients_sum()).strip()
                + " over the entire simulation."
            )
            print(
                "         The outdoor crop production to satisfy this before waste comes to "
                + str(
                    outdoor_crops.production.get_nutrients_sum()
                    / (1 - outdoor_crops.CROP_WASTE / 100)
                ).strip()
                + " over the entire simulation."
            )
            print(
                "         The stored food available before waste at the start of the simulation is "
                + str(
                    stored_food.initial_available / (1 - outdoor_crops.CROP_WASTE / 100)
                ).strip()
                + "."
            )
            print(
                "         This results in a net deficit of calories (after using up all stored food) of:"
                + str(-stored_food.initial_available_to_humans).strip()
            )
            print("Setting stored food to zero!")
            print(
                "(The resulting graph shown and percent people fed is therefore also likely unrealistic.)"
            )
            print("")

            # Set stored food to zero
            stored_food.initial_available_to_humans.new_food_just_from_kcals()

        time_consts["seaweed"] = seaweed
        time_consts["methane_scp"] = methane_scp
        time_consts["cellulosic_sugar"] = cellulosic_sugar
        time_consts["outdoor_crops"] = outdoor_crops
        constants_out["stored_food"] = stored_food

        return (time_consts, constants_out, feed_and_biofuels)

    def calculate_biofuel_components_without_stored_food(
        self,
        include_fat_or_protein,
        biofuels_before_cap_prewaste,
        seaweed,
        cellulosic_sugar,
        methane_scp,
        outdoor_crops,
    ):
        assert not include_fat_or_protein, """ERROR:" biofuel calculations are not 
        working  yet for scenarios including fat or protein"""

        # first, preference seaweed, then cellulosic_sugar, then methane_scp

        # TODO: ADD SEAWEED
        # cell sugar

        cell_sugar_for_biofuel = (
            cellulosic_sugar.MAX_FRACTION_BIOFUEL_CONSUMED_AS_CELLULOSIC_SUGAR
            * biofuels_before_cap_prewaste.kcals
        )

        # minimum between elements of two 1d arrays
        cell_sugar_for_biofuel_after_limit = np.min(
            [cell_sugar_for_biofuel, cellulosic_sugar.production.kcals], axis=0
        )

        cellulosic_sugar_used_for_biofuel = np.min(
            [cell_sugar_for_biofuel_after_limit, biofuels_before_cap_prewaste.kcals],
            axis=0,
        )

        remaining_biofuel_needed = np.subtract(
            biofuels_before_cap_prewaste.kcals, cellulosic_sugar_used_for_biofuel
        )

        # methanescp

        methane_scp_for_biofuel = (
            methane_scp.MAX_FRACTION_BIOFUEL_CONSUMED_AS_SCP * remaining_biofuel_needed
        )

        methane_scp_for_biofuel_after_limit = np.min(
            [methane_scp_for_biofuel, methane_scp.production.kcals], axis=0
        )

        methane_scp_used_for_biofuel = np.min(
            [methane_scp_for_biofuel_after_limit, remaining_biofuel_needed], axis=0
        )

        remaining_biofuel_needed = np.subtract(
            biofuels_before_cap_prewaste.kcals, methane_scp_used_for_biofuel
        )

        # outdoor growing

        outdoor_crops_used_for_biofuel_before_shift = np.min(
            [outdoor_crops.production.kcals, remaining_biofuel_needed], axis=0
        )

        remaining_biofuel_needed_kcals_before_shift = np.subtract(
            biofuels_before_cap_prewaste.kcals,
            outdoor_crops_used_for_biofuel_before_shift,
        )

        outdoor_crops_remaining_after_biofuel_before_shift = (
            outdoor_crops.production.kcals - outdoor_crops_used_for_biofuel_before_shift
        )

        # THE SHIFT AND SUBTRACT (ALLOWING STORED FOOD FROM OUTDOOR GROWING TO BE USED) IS BELOW

        (
            outdoor_crops_remaining_after_biofuel,
            remaining_biofuel_needed_from_stored_food,
            outdoor_crops_used_for_biofuel_stored_6months,
        ) = self.subtract_off_usage_iteratively(
            remaining_biofuel_needed_kcals_before_shift,
            outdoor_crops_remaining_after_biofuel_before_shift,
        )

        outdoor_crops_used_for_biofuel = (
            outdoor_crops_used_for_biofuel_stored_6months
            + outdoor_crops_used_for_biofuel_before_shift
        )

        outdoor_crops_remaining_after_biofuel = np.subtract(
            outdoor_crops.production.kcals,
            outdoor_crops_used_for_biofuel,
        )

        return (
            outdoor_crops_remaining_after_biofuel,
            remaining_biofuel_needed_from_stored_food,
            outdoor_crops_used_for_biofuel,
            methane_scp_used_for_biofuel,
            cellulosic_sugar_used_for_biofuel,
        )

    def calculate_feed_components_without_stored_food(
        self,
        include_fat_or_protein,
        feeds_before_cap_prewaste,
        max_fraction_feed_consumed_as_cellulosic_sugar,
        max_fraction_feed_consumed_as_methane_scp,
        cellulosic_sugar_remaining_after_biofuel,
        methane_scp_remaining_after_biofuel,
        outdoor_crops_remaining_after_biofuel,
    ):
        assert not include_fat_or_protein, """ERROR: feed calculations are not 
        working  yet for scenarios including fat or protein"""

        # first, preference seaweed, then cellulosic_sugar, then methane_scp
        # this is used to reduce these food sources by the amount the feed
        # is used in each month
        # TODO: MAKE WORK WITH FAT AND PROTEIN
        # TODO: ADD SEAWEED
        # cell sugar

        cell_sugar_for_feed = (
            max_fraction_feed_consumed_as_cellulosic_sugar
            * feeds_before_cap_prewaste.kcals
        )

        cell_sugar_for_feed_after_limit = np.min(
            [cell_sugar_for_feed, cellulosic_sugar_remaining_after_biofuel], axis=0
        )

        cellulosic_sugar_used_for_feed = np.min(
            [cell_sugar_for_feed_after_limit, feeds_before_cap_prewaste.kcals], axis=0
        )

        remaining_feed_needed = np.subtract(
            feeds_before_cap_prewaste.kcals, cellulosic_sugar_used_for_feed
        )

        # methanescp

        methane_scp_for_feed = (
            max_fraction_feed_consumed_as_methane_scp * remaining_feed_needed
        )

        methane_scp_for_feed_after_limit = np.min(
            [methane_scp_for_feed, methane_scp_remaining_after_biofuel], axis=0
        )

        methane_scp_used_for_feed = np.min(
            [methane_scp_for_feed_after_limit, remaining_feed_needed], axis=0
        )

        remaining_feed_needed = np.subtract(
            feeds_before_cap_prewaste.kcals, methane_scp_used_for_feed
        )

        # outdoor growing
        outdoor_crops_used_for_feed_before_shift = np.min(
            [outdoor_crops_remaining_after_biofuel, remaining_feed_needed], axis=0
        )

        # this is the amount of kcals that all the combined sources could not fulfill
        # in each month
        # TODO: deal with nutrients...
        remaining_feed_needed_kcals_before_shift = np.subtract(
            feeds_before_cap_prewaste.kcals,
            outdoor_crops_used_for_feed_before_shift,
        )

        # now that we have outdoor crops bottomed out in the winter seasons, let's also subtract off some of the outdoor
        # crops in the high production seasons, if there is any remaining feed needed
        # (because sometimes theres not enough stored food initial at start of the simulation to make up for all the
        # lacking food needed for feed)

        # there will be a bit of an offset here: the outdoor crops from months 12+ will be reduced by the amount of
        # remaining feed needed. So we introduce a 6 month shift,
        # so that the outdoor crops are moved forward in time by 6 months, and the feed is subtracted off.

        outdoor_crops_remaining_after_feed_and_biofuel_before_shift = (
            outdoor_crops_remaining_after_biofuel
            - outdoor_crops_used_for_feed_before_shift
        )

        # THE SHIFT AND SUBTRACT (ALLOWING STORED FOOD FROM OUTDOOR GROWING TO BE USED) IS BELOW

        (
            outdoor_crops_remaining_after_feed_and_biofuel,
            remaining_feed_needed_from_stored_food,
            outdoor_crops_used_for_feed_stored_6months,
        ) = self.subtract_off_usage_iteratively(
            remaining_feed_needed_kcals_before_shift,
            outdoor_crops_remaining_after_feed_and_biofuel_before_shift,
        )

        outdoor_crops_used_for_feed = (
            outdoor_crops_used_for_feed_stored_6months
            + outdoor_crops_used_for_feed_before_shift
        )

        # TO NOT DO THE SHIFT (may fail to have enough stored food...:

        # # (
        # #     outdoor_crops_remaining_after_feed_and_biofuel,
        # #     remaining_feed_needed_kcals,
        # #     outdoor_crops_used_for_feed_stored_6months,
        # # ) = self.subtract_off_feed_from_6mo_previous_outdoor_growing(
        # #     remaining_feed_needed_kcals_before_shift,
        # #     outdoor_crops_remaining_after_feed_and_biofuel_before_shift,
        # # )

        # outdoor_crops_remaining_after_feed_and_biofuel = (
        #     outdoor_crops_remaining_after_feed_and_biofuel_before_shift
        # )
        # remaining_feed_needed_kcals = remaining_feed_needed_kcals_before_shift

        # outdoor_crops_used_for_feed = (
        #     # outdoor_crops_used_for_feed_stored_6months
        #     +outdoor_crops_used_for_feed_before_shift
        # )

        # remaining_feed_needed_from_stored_food = Food(
        #     kcals=np.array(remaining_feed_needed_kcals),
        #     fat=np.zeros(len(remaining_feed_needed_kcals)),
        #     protein=np.zeros(len(remaining_feed_needed_kcals)),
        #     kcals_units="billion kcals each month",
        #     fat_units="thousand tons each month",
        #     protein_units="thousand tons each month",
        # )

        return (
            outdoor_crops_remaining_after_feed_and_biofuel,
            remaining_feed_needed_from_stored_food,
            outdoor_crops_used_for_feed,
            methane_scp_used_for_feed,
            cellulosic_sugar_used_for_feed,
        )

    def subtract_off_usage_iteratively(
        self,
        remaining_usage_needed_kcals,
        outdoor_crops_remaining,
        max_shift=12,
    ):
        total_calories_init = np.sum(outdoor_crops_remaining) - np.sum(
            remaining_usage_needed_kcals
        )

        total_outdoor_crops_used = np.zeros_like(remaining_usage_needed_kcals)

        for shift in range(1, max_shift):
            (
                outdoor_crops_remaining,
                remaining_usage_needed_kcals,
                outdoor_crops_used_for_this_shift,
            ) = self.subtract_off_usage_by_storing_outdoor_growing(
                remaining_usage_needed_kcals,
                outdoor_crops_remaining,
                shift,
            )
            total_outdoor_crops_used += outdoor_crops_used_for_this_shift

        total_calories_final = np.sum(outdoor_crops_remaining) - np.sum(
            remaining_usage_needed_kcals
        )

        assert abs(total_calories_init - total_calories_final) < 1e-4

        remaining_usage_needed_from_stored_food = Food(
            kcals=np.array(remaining_usage_needed_kcals),
            fat=np.zeros(len(remaining_usage_needed_kcals)),
            protein=np.zeros(len(remaining_usage_needed_kcals)),
            kcals_units="billion kcals each month",
            fat_units="thousand tons each month",
            protein_units="thousand tons each month",
        )

        return (
            outdoor_crops_remaining,
            remaining_usage_needed_from_stored_food,
            total_outdoor_crops_used,
        )

    def subtract_off_usage_by_storing_outdoor_growing(
        self,
        remaining_usage_needed_kcals_before_shift,
        outdoor_crops_remaining_before_shift,
        MONTH_SHIFT,
    ):
        # now that we have outdoor crops bottomed out in the winter seasons, let's also subtract off some of the
        # outdoor crops in the high production seasons, if there is any remaining usage needed
        # (because sometimes theres not enough stored food initial at start of the simulation to make up for all the
        # lacking food needed for usage)

        # there will be a bit of an offset here: the outdoor crops from months 12+ will be reduced by the amount of
        # remaining usage needed. So we introduce a 6 month shift, so that the outdoor
        # crops are moved forward in time by 6 months, and the usage is subtracted off.

        # mask off stored food we don't want to use to zero (if available food at a given month is zero, it won't
        # be used)
        masked_remaining_food = np.concatenate(
            [
                outdoor_crops_remaining_before_shift[:-MONTH_SHIFT],
                np.zeros(MONTH_SHIFT),
            ]
        )

        # move the available food 6 months into the future
        outdoor_crops_which_can_be_used_later = np.roll(
            masked_remaining_food, MONTH_SHIFT
        )

        assert len(masked_remaining_food) == len(outdoor_crops_which_can_be_used_later)

        # get the amount which could be used for usage. Only use the amount that is needed, but not more than can
        # be supplied.
        outdoor_crops_used_for_usage_stored_shifted = np.min(
            [
                outdoor_crops_which_can_be_used_later,
                remaining_usage_needed_kcals_before_shift,
            ],
            axis=0,
        )

        # the remaining usage needed is reduced for the months they are used (6 months after production)
        remaining_usage_needed_kcals = np.subtract(
            remaining_usage_needed_kcals_before_shift,
            outdoor_crops_used_for_usage_stored_shifted,
        )

        # the amount of outdoor crops used is applied 6 months prior. Because first 12 months were masked out,this
        # can't subtract from food at the end of the period
        outdoor_crops_used_for_usage_stored_shifted = np.roll(
            outdoor_crops_used_for_usage_stored_shifted, -MONTH_SHIFT
        )
        outdoor_crops_remaining = (
            outdoor_crops_remaining_before_shift
            - outdoor_crops_used_for_usage_stored_shifted
        )

        return (
            outdoor_crops_remaining,
            remaining_usage_needed_kcals,
            outdoor_crops_used_for_usage_stored_shifted,
        )

    def init_meat_and_dairy_and_feed_from_breeding(
        self,
        constants_inputs,
        reduction_in_dairy_calves,
        use_grass_and_residues_for_dairy,
        cao,
        feed_and_biofuels,
        meat_and_dairy,
        feed_ratio,
        constants_out,
        time_consts,
    ):
        if constants_inputs["REDUCED_BREEDING_STRATEGY"]:
            data = {
                "country_code": constants_inputs["COUNTRY_CODE"],
                "reduction_in_beef_calves": 90,
                "reduction_in_dairy_calves": reduction_in_dairy_calves,
                "increase_in_slaughter": 110,
                "reduction_in_pig_breeding": 90,
                "reduction_in_poultry_breeding": 90,
                "months": constants_inputs["NMONTHS"],
                "discount_rate": 30,
                "mother_slaughter": 0,
                "use_grass_and_residues_for_dairy": use_grass_and_residues_for_dairy,
                "keep_dairy": True,
                "feed_ratio": feed_ratio,
            }
        else:
            data = {
                "country_code": constants_inputs["COUNTRY_CODE"],
                "reduction_in_beef_calves": 0,
                "reduction_in_dairy_calves": 0,
                "increase_in_slaughter": 100,
                "reduction_in_pig_breeding": 0,
                "reduction_in_poultry_breeding": 0,
                "months": constants_inputs["NMONTHS"],
                "discount_rate": 0,
                "mother_slaughter": 0,
                "use_grass_and_residues_for_dairy": use_grass_and_residues_for_dairy,
                "keep_dairy": True,
                "feed_ratio": feed_ratio,
            }

        feed_dairy_meat_results, feed = cao.calculate_feed_and_animals(data)
        # MEAT AND DAIRY from breeding reduction strategy

        meat_and_dairy.calculate_meat_nutrition()

        (
            constants_out["culled_meat"],
            constants_out["CULLED_MEAT_FRACTION_FAT"],
            constants_out["CULLED_MEAT_FRACTION_PROTEIN"],
        ) = meat_and_dairy.calculate_culled_meat(
            np.sum(feed_dairy_meat_results["Poultry Slaughtered"]),
            np.sum(feed_dairy_meat_results["Pig Slaughtered"]),
            np.sum(feed_dairy_meat_results["Beef Slaughtered"]),
        )

        time_consts["max_culled_kcals"] = meat_and_dairy.get_max_slaughter_monthly(
            feed_dairy_meat_results["Beef Slaughtered"],
            feed_dairy_meat_results["Pig Slaughtered"],
            feed_dairy_meat_results["Poultry Slaughtered"],
        )
        # https://www.nass.usda.gov/Charts_and_Maps/Milk_Production_and_Milk_Cows/cowrates.php
        monthly_milk_tons = (
            feed_dairy_meat_results["Dairy Pop"]
            * 24265
            / 2.2046
            / 365
            * 30.4
            / 1000
            / 2
        )
        # cows * pounds per cow per day * punds_to_kg /days in year * days in month /
        # kg_in_tons * ratio_milk_producing_cows
        PRINT_ANNUAL_POUNDS_MILK = False
        if PRINT_ANNUAL_POUNDS_MILK:
            print("annual pounds milk")  # ton to kg, kg to pounds, monthly to annual
            print(
                monthly_milk_tons * 1000 * 2.2046 * 12
            )  # ton to kg, kg to pounds, monthly to annual

        (
            grazing_milk_kcals,
            grazing_milk_fat,
            grazing_milk_protein,
        ) = meat_and_dairy.get_grazing_milk_produced_postwaste(monthly_milk_tons)

        time_consts["grazing_milk_kcals"] = grazing_milk_kcals
        time_consts["grazing_milk_fat"] = grazing_milk_fat
        time_consts["grazing_milk_protein"] = grazing_milk_protein

        time_consts["cattle_grazing_maintained_kcals"] = np.zeros(
            constants_inputs["NMONTHS"]
        )
        time_consts["cattle_grazing_maintained_fat"] = np.zeros(
            constants_inputs["NMONTHS"]
        )
        time_consts["cattle_grazing_maintained_protein"] = np.zeros(
            constants_inputs["NMONTHS"]
        )

        (
            constants_out["KG_PER_SMALL_ANIMAL"],
            constants_out["KG_PER_MEDIUM_ANIMAL"],
            constants_out["KG_PER_LARGE_ANIMAL"],
            constants_out["LARGE_ANIMAL_KCALS_PER_KG"],
            constants_out["LARGE_ANIMAL_FAT_RATIO"],
            constants_out["LARGE_ANIMAL_PROTEIN_RATIO"],
            constants_out["MEDIUM_ANIMAL_KCALS_PER_KG"],
            constants_out["SMALL_ANIMAL_KCALS_PER_KG"],
        ) = meat_and_dairy.get_meat_nutrition()

        time_consts["grain_fed_meat_kcals"] = np.zeros(constants_inputs["NMONTHS"])
        time_consts["grain_fed_meat_fat"] = np.zeros(constants_inputs["NMONTHS"])
        time_consts["grain_fed_meat_protein"] = np.zeros(constants_inputs["NMONTHS"])
        time_consts["grain_fed_milk_kcals"] = np.zeros(constants_inputs["NMONTHS"])
        time_consts["grain_fed_milk_fat"] = np.zeros(constants_inputs["NMONTHS"])
        time_consts["grain_fed_milk_protein"] = np.zeros(constants_inputs["NMONTHS"])

        time_consts["grain_fed_created_kcals"] = np.zeros(constants_inputs["NMONTHS"])
        time_consts["grain_fed_created_fat"] = np.zeros(constants_inputs["NMONTHS"])
        time_consts["grain_fed_created_protein"] = np.zeros(constants_inputs["NMONTHS"])

        # FEED AND BIOFUELS from breeding reduction strategy

        (
            biofuels_before_cap_prewaste,
            feed_before_cap_prewaste,
            excess_feed_prewaste,
        ) = feed_and_biofuels.get_biofuels_and_feed_before_waste_from_animal_pops(
            constants_inputs,
            feed,
        )

        feed_and_biofuels.nonhuman_consumption = (
            biofuels_before_cap_prewaste + feed_before_cap_prewaste
        )

        PLOT_FEED_BEFORE_WASTE = False

        if PLOT_FEED_BEFORE_WASTE:
            feed_before_cap_prewaste.in_units_percent_fed().plot(
                "feed_before_cap_prewaste"
            )

        time_consts["excess_feed"] = excess_feed_prewaste

        return (
            biofuels_before_cap_prewaste,
            feed_before_cap_prewaste,
            meat_and_dairy,
            time_consts,
            constants_out,
        )

    def init_meat_and_dairy_params(
        self,
        constants_inputs,
        constants_out,
        time_consts,
        feed_and_biofuels,
        outdoor_crops,
    ):
        """
        Meat and dairy are initialized here.
        NOTE: Important convention: anything pre-waste is marked so. Everything else
              that could include waste should be assumed to be post-waste if not marked

        """

        meat_and_dairy = MeatAndDairy(constants_inputs)
        meat_and_dairy.calculate_meat_nutrition()

        time_consts, meat_and_dairy = self.init_grazing_params(
            constants_inputs, time_consts, meat_and_dairy
        )

        time_consts, meat_and_dairy = self.init_grain_fed_meat_params(
            time_consts,
            meat_and_dairy,
            feed_and_biofuels,
            constants_inputs,
            outdoor_crops,
        )

        (
            constants_out,
            time_consts,
            meat_and_dairy,
        ) = self.init_culled_meat_params(
            constants_inputs, constants_out, time_consts, meat_and_dairy
        )

        return meat_and_dairy, constants_out, time_consts

    def init_grazing_params(self, constants_inputs, time_consts, meat_and_dairy):
        if constants_inputs["USE_EFFICIENT_FEED_STRATEGY"]:
            meat_and_dairy.calculate_meat_milk_from_human_inedible_feed(
                constants_inputs
            )
        else:
            meat_and_dairy.calculate_continued_ratios_meat_dairy_grazing(
                constants_inputs
            )

        (
            grazing_milk_kcals,
            grazing_milk_fat,
            grazing_milk_protein,
        ) = meat_and_dairy.get_grazing_milk_produced_postwaste(
            meat_and_dairy.grazing_milk_produced_prewaste
        )

        time_consts["grazing_milk_kcals"] = grazing_milk_kcals
        time_consts["grazing_milk_fat"] = grazing_milk_fat
        time_consts["grazing_milk_protein"] = grazing_milk_protein

        # Post-waste cattle ongoing meat production from grazing
        (
            cattle_grazing_maintained_kcals,
            cattle_grazing_maintained_fat,
            cattle_grazing_maintained_protein,
        ) = meat_and_dairy.get_cattle_grazing_maintained()

        time_consts["cattle_grazing_maintained_kcals"] = cattle_grazing_maintained_kcals
        time_consts["cattle_grazing_maintained_fat"] = cattle_grazing_maintained_fat
        time_consts[
            "cattle_grazing_maintained_protein"
        ] = cattle_grazing_maintained_protein

        return time_consts, meat_and_dairy

    def init_grain_fed_meat_params(
        self,
        time_consts,
        meat_and_dairy,
        feed_and_biofuels,
        constants_inputs,
        outdoor_crops,
    ):
        # APPLY FEED+BIOFUEL WASTE here
        # this is because the total contributed by feed and biofuels is actually
        # applied to
        # the crops and stored food before waste, which means the subtraction of waste
        # happens
        # to the feed and biofuels before subtracting from stored food and crops.
        # any reasonable cap of production should reflect a cap on the actual amount
        # available
        # to humans.

        # "grain" in all cases just means the stored food + outdoor crop production
        # that is human edible and used for feed
        # this calculation is pre-waste for meat and feed
        # Chicken and pork only ever use "grain" as defined above in this model, not
        # grasses

        if constants_inputs["USE_EFFICIENT_FEED_STRATEGY"]:
            meat_and_dairy.calculate_meat_and_dairy_from_grain(
                feed_and_biofuels.fed_to_animals_prewaste
            )
        else:
            meat_and_dairy.calculate_continued_ratios_meat_dairy_grain(
                feed_and_biofuels.fed_to_animals_prewaste, outdoor_crops
            )
        # this calculation is pre-waste for the feed
        # no waste is applied for the grasses either.
        # the milk has had waste applied
        (
            grain_fed_milk_kcals,
            grain_fed_milk_fat,
            grain_fed_milk_protein,
        ) = meat_and_dairy.get_milk_from_human_edible_feed(constants_inputs)

        # post waste
        (
            grain_fed_meat_kcals,
            grain_fed_meat_fat,
            grain_fed_meat_protein,
        ) = meat_and_dairy.get_meat_from_human_edible_feed()

        time_consts["grain_fed_meat_kcals"] = grain_fed_meat_kcals
        time_consts["grain_fed_meat_fat"] = grain_fed_meat_fat
        time_consts["grain_fed_meat_protein"] = grain_fed_meat_protein
        time_consts["grain_fed_milk_kcals"] = grain_fed_milk_kcals
        time_consts["grain_fed_milk_fat"] = grain_fed_milk_fat
        time_consts["grain_fed_milk_protein"] = grain_fed_milk_protein

        grain_fed_created_kcals = grain_fed_meat_kcals + grain_fed_milk_kcals
        grain_fed_created_fat = grain_fed_meat_fat + grain_fed_milk_fat
        grain_fed_created_protein = grain_fed_meat_protein + grain_fed_milk_protein
        time_consts["grain_fed_created_kcals"] = grain_fed_created_kcals
        time_consts["grain_fed_created_fat"] = grain_fed_created_fat
        time_consts["grain_fed_created_protein"] = grain_fed_created_protein

        feed = feed_and_biofuels.feed

        if (grain_fed_created_kcals <= 0).any():
            grain_fed_created_kcals = grain_fed_created_kcals.round(8)
        assert (grain_fed_created_kcals >= 0).all()

        if (grain_fed_created_fat <= 0).any():
            grain_fed_created_fat = grain_fed_created_fat.round(8)
        assert (grain_fed_created_fat >= 0).all()

        if (grain_fed_created_protein <= 0).any():
            grain_fed_created_protein = grain_fed_created_protein.round(8)
        assert (grain_fed_created_protein >= 0).all()

        # True if reproducing xia et al results when directly subtracting feed from
        # produced crops
        SUBTRACTING_FEED_DIRECTLY_FROM_PRODUCTION = False
        if not SUBTRACTING_FEED_DIRECTLY_FROM_PRODUCTION:
            assert (feed.kcals >= grain_fed_created_kcals).all()

        return time_consts, meat_and_dairy

    def init_culled_meat_params(
        self, constants_inputs, constants_out, time_consts, meat_and_dairy
    ):
        # culled meat is based on the amount that wouldn't be maintained (excluding
        # maintained cattle as well as maintained chicken and pork)
        # this calculation is pre-waste for the meat maintained of course (no waste
        # applied to livestock maintained counts from which we determined the amount
        # of meat which can be culled)
        # the actual culled meat returned is post waste
        # NOTE: in the future, the extra caloric gain in reducing livestock populations
        #       slowly and caloric loss from increasing livestock populations slowly
        #       should also be calculated
        meat_and_dairy.calculate_animals_culled(constants_inputs)
        (
            meat_and_dairy.initial_culled_meat_prewaste,
            constants_out["CULLED_MEAT_FRACTION_FAT"],
            constants_out["CULLED_MEAT_FRACTION_PROTEIN"],
        ) = meat_and_dairy.calculate_culled_meat(
            meat_and_dairy.init_small_animals_culled,
            meat_and_dairy.init_medium_animals_culled,
            meat_and_dairy.init_large_animals_culled,
        )

        MAX_RATIO_CULLED_SLAUGHTER_TO_BASELINE = constants_inputs[
            "MAX_RATIO_CULLED_SLAUGHTER_TO_BASELINE"
        ]
        culled_meat = meat_and_dairy.get_culled_meat_post_waste(constants_inputs)

        time_consts["max_culled_kcals"] = meat_and_dairy.calculate_meat_limits(
            MAX_RATIO_CULLED_SLAUGHTER_TO_BASELINE, culled_meat
        )
        constants_out["culled_meat"] = culled_meat

        (
            constants_out["KG_PER_SMALL_ANIMAL"],
            constants_out["KG_PER_MEDIUM_ANIMAL"],
            constants_out["KG_PER_LARGE_ANIMAL"],
            constants_out["LARGE_ANIMAL_KCALS_PER_KG"],
            constants_out["LARGE_ANIMAL_FAT_RATIO"],
            constants_out["LARGE_ANIMAL_PROTEIN_RATIO"],
            constants_out["MEDIUM_ANIMAL_KCALS_PER_KG"],
            constants_out["SMALL_ANIMAL_KCALS_PER_KG"],
        ) = meat_and_dairy.get_meat_nutrition()

        return (constants_out, time_consts, meat_and_dairy)
