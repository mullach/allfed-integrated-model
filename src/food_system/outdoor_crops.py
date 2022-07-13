################################# Outdoor Crops ###############################
##                                                                            #
##       Functions and constants relating to outdoor crop production          #
##    IMPORTANT NOTE: CROP WASTE *IS* SUBTRACTED, BUT IT'S IN THE OPTIMIZER   #
##                                                                            #
###############################################################################

import numpy as np


class OutdoorCrops:
    def __init__(self, inputs_to_optimizer):

        self.NMONTHS = inputs_to_optimizer["NMONTHS"]
        self.STARTING_MONTH_NUM = inputs_to_optimizer["STARTING_MONTH_NUM"]

        self.BASELINE_CROP_KCALS = inputs_to_optimizer["BASELINE_CROP_KCALS"]
        self.BASELINE_CROP_FAT = inputs_to_optimizer["BASELINE_CROP_FAT"]
        self.BASELINE_CROP_PROTEIN = inputs_to_optimizer["BASELINE_CROP_PROTEIN"]

        self.ADD_OUTDOOR_GROWING = inputs_to_optimizer["ADD_OUTDOOR_GROWING"]
        # FAO ALL SUPPLY UTILIZATION SHEET
        # units are millions tons (dry caloric, fat, protein)
        #         year    Kcals    Fat    Protein
        #         2014    3550    225    468
        #         2015    3583    228    478
        #         2016    3682    234    493
        #         2017    3774    246    511
        #         2018    3725    245    498
        #         2019    7087    449    937

        # TREND    2020    3879.2    257    525
        # percent OG redirected to non-eaten seeds
        self.SEED_PERCENT = 100 * (92 / 3898)

        # tonnes dry carb equivalent
        self.ANNUAL_YIELD = (
            0.96 * self.BASELINE_CROP_KCALS * (1 - self.SEED_PERCENT / 100)
        )

        # 1000 tons fat per billion kcals
        self.OG_FRACTION_FAT = (
            1.02 * (self.BASELINE_CROP_FAT / 1e3) / (self.ANNUAL_YIELD * 4e6 / 1e9)
        )

        # 1000 tons protein per billion kcals
        self.OG_FRACTION_PROTEIN = (
            0.93 * (self.BASELINE_CROP_PROTEIN / 1e3) / (self.ANNUAL_YIELD * 4e6 / 1e9)
        )
        print("protein 1000 tons BASELINE_CROP_PROTEIN / 1e3")
        print(self.BASELINE_CROP_PROTEIN / 1e3)
        print("billion kcals ANNUAL_YIELD * 4e6 / 1e9")
        print(self.ANNUAL_YIELD * 4e6 / 1e9)
        print("self.OG_FRACTION_PROTEIN")
        print(self.OG_FRACTION_PROTEIN)

    def calculate_rotation_ratios(self, inputs_to_optimizer):

        # need to use the multiplier on units of kcals to get fat and protein
        if inputs_to_optimizer["OG_USE_BETTER_ROTATION"]:

            # deals with the issue of caloric improvement being more than
            # present-day production during the beginning months
            # of the simulation.
            self.OG_KCAL_REDUCED = inputs_to_optimizer["ROTATION_IMPROVEMENTS"][
                "KCALS_REDUCTION"
            ]

            self.OG_ROTATION_FRACTION_KCALS = 1

            self.KCAL_RATIO_ROT = 1
            self.FAT_ROTATION_RATIO = inputs_to_optimizer["ROTATION_IMPROVEMENTS"][
                "FAT_RATIO"
            ]
            self.PROTEIN_ROTATION_RATIO = inputs_to_optimizer["ROTATION_IMPROVEMENTS"][
                "PROTEIN_RATIO"
            ]

            self.OG_ROTATION_FRACTION_FAT = (
                self.OG_FRACTION_FAT * self.FAT_ROTATION_RATIO
            )
            self.OG_ROTATION_FRACTION_PROTEIN = (
                self.OG_FRACTION_PROTEIN * self.PROTEIN_ROTATION_RATIO
            )

            self.FAT_RATIO_ROT = self.OG_ROTATION_FRACTION_FAT
            self.PROTEIN_RATIO_ROT = self.OG_ROTATION_FRACTION_PROTEIN

        else:
            self.OG_KCAL_REDUCED = 1
            self.OG_ROTATION_FRACTION_KCALS = 1
            self.OG_ROTATION_FRACTION_FAT = self.OG_FRACTION_FAT
            self.OG_ROTATION_FRACTION_PROTEIN = self.OG_FRACTION_PROTEIN

            self.KCAL_RATIO_ROT = 1
            self.FAT_RATIO_ROT = self.OG_FRACTION_FAT
            self.PROTEIN_RATIO_ROT = self.OG_FRACTION_PROTEIN

    def calculate_monthly_production(self, inputs_to_optimizer):
        # assumption: outdoor crop production is very similar in nutritional
        # profile to stored food
        # reference: row 11, 'outputs' tab
        # @ Morgan: Link here was dead, please add again
        # @ Florian: https://docs.google.com/spreadsheets/d/19kzHpux690JTCo2IX2UA1faAd7R1QcBK/edit#gid=1815939673
        #            does that link work for you?
        month_index = self.STARTING_MONTH_NUM - 1

        JAN_FRACTION = inputs_to_optimizer["SEASONALITY"][0]
        FEB_FRACTION = inputs_to_optimizer["SEASONALITY"][1]
        MAR_FRACTION = inputs_to_optimizer["SEASONALITY"][2]
        APR_FRACTION = inputs_to_optimizer["SEASONALITY"][3]
        MAY_FRACTION = inputs_to_optimizer["SEASONALITY"][4]
        JUN_FRACTION = inputs_to_optimizer["SEASONALITY"][5]
        JUL_FRACTION = inputs_to_optimizer["SEASONALITY"][6]
        AUG_FRACTION = inputs_to_optimizer["SEASONALITY"][7]
        SEP_FRACTION = inputs_to_optimizer["SEASONALITY"][8]
        OCT_FRACTION = inputs_to_optimizer["SEASONALITY"][9]
        NOV_FRACTION = inputs_to_optimizer["SEASONALITY"][10]
        DEC_FRACTION = inputs_to_optimizer["SEASONALITY"][11]

        # tons dry carb equivalent
        JAN_YIELD = JAN_FRACTION * self.ANNUAL_YIELD
        FEB_YIELD = FEB_FRACTION * self.ANNUAL_YIELD
        MAR_YIELD = MAR_FRACTION * self.ANNUAL_YIELD
        APR_YIELD = APR_FRACTION * self.ANNUAL_YIELD
        MAY_YIELD = MAY_FRACTION * self.ANNUAL_YIELD
        JUN_YIELD = JUN_FRACTION * self.ANNUAL_YIELD
        JUL_YIELD = JUL_FRACTION * self.ANNUAL_YIELD
        AUG_YIELD = AUG_FRACTION * self.ANNUAL_YIELD
        SEP_YIELD = SEP_FRACTION * self.ANNUAL_YIELD
        OCT_YIELD = OCT_FRACTION * self.ANNUAL_YIELD
        NOV_YIELD = NOV_FRACTION * self.ANNUAL_YIELD
        DEC_YIELD = DEC_FRACTION * self.ANNUAL_YIELD

        # billions of kcals
        JAN_KCALS_OG = JAN_YIELD * 4e6 / 1e9
        FEB_KCALS_OG = FEB_YIELD * 4e6 / 1e9
        MAR_KCALS_OG = MAR_YIELD * 4e6 / 1e9
        APR_KCALS_OG = APR_YIELD * 4e6 / 1e9
        MAY_KCALS_OG = MAY_YIELD * 4e6 / 1e9
        JUN_KCALS_OG = JUN_YIELD * 4e6 / 1e9
        JUL_KCALS_OG = JUL_YIELD * 4e6 / 1e9
        AUG_KCALS_OG = AUG_YIELD * 4e6 / 1e9
        SEP_KCALS_OG = SEP_YIELD * 4e6 / 1e9
        OCT_KCALS_OG = OCT_YIELD * 4e6 / 1e9
        NOV_KCALS_OG = NOV_YIELD * 4e6 / 1e9
        DEC_KCALS_OG = DEC_YIELD * 4e6 / 1e9

        RATIO_KCALS_POSTDISASTER_1Y = 1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR1"]
        RATIO_KCALS_POSTDISASTER_2Y = 1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR2"]
        RATIO_KCALS_POSTDISASTER_3Y = 1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR3"]
        RATIO_KCALS_POSTDISASTER_4Y = 1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR4"]
        RATIO_KCALS_POSTDISASTER_5Y = 1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR5"]
        RATIO_KCALS_POSTDISASTER_6Y = 1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR6"]
        RATIO_KCALS_POSTDISASTER_7Y = 1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR7"]
        RATIO_KCALS_POSTDISASTER_8Y = 1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR8"]
        RATIO_KCALS_POSTDISASTER_9Y = 1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR9"]
        RATIO_KCALS_POSTDISASTER_10Y = (
            1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR10"]
        )
        RATIO_KCALS_POSTDISASTER_11Y = (
            1 - inputs_to_optimizer["DISRUPTION_CROPS_YEAR11"]
        )

        first_year_starting_point = [1] * self.STARTING_MONTH_NUM
        y1_to_y2 = np.linspace(1, RATIO_KCALS_POSTDISASTER_1Y, 13)[1:]
        y2_to_y3 = np.linspace(
            RATIO_KCALS_POSTDISASTER_1Y, RATIO_KCALS_POSTDISASTER_2Y, 13
        )[1:]
        y3_to_y4 = np.linspace(
            RATIO_KCALS_POSTDISASTER_2Y, RATIO_KCALS_POSTDISASTER_3Y, 13
        )[1:]
        y4_to_y5 = np.linspace(
            RATIO_KCALS_POSTDISASTER_3Y, RATIO_KCALS_POSTDISASTER_4Y, 13
        )[1:]
        y5_to_y6 = np.linspace(
            RATIO_KCALS_POSTDISASTER_4Y, RATIO_KCALS_POSTDISASTER_5Y, 13
        )[1:]
        y6_to_y7 = np.linspace(
            RATIO_KCALS_POSTDISASTER_5Y, RATIO_KCALS_POSTDISASTER_6Y, 13
        )[1:]
        y7_to_y8 = np.linspace(
            RATIO_KCALS_POSTDISASTER_6Y, RATIO_KCALS_POSTDISASTER_7Y, 13
        )[1:]
        y8_to_y9 = np.linspace(
            RATIO_KCALS_POSTDISASTER_7Y, RATIO_KCALS_POSTDISASTER_8Y, 13
        )[1:]
        y9_to_y10 = np.linspace(
            RATIO_KCALS_POSTDISASTER_8Y, RATIO_KCALS_POSTDISASTER_9Y, 13
        )[1:]
        y10_to_y11 = np.linspace(
            RATIO_KCALS_POSTDISASTER_9Y, RATIO_KCALS_POSTDISASTER_10Y, 13
        )[1:]
        y11_to_y11 = np.linspace(
            RATIO_KCALS_POSTDISASTER_10Y, RATIO_KCALS_POSTDISASTER_11Y, 13
        )[1 : 12 - (month_index)]

        self.all_months_reductions = np.array(
            first_year_starting_point
            + list(y1_to_y2)
            + list(y2_to_y3)
            + list(y3_to_y4)
            + list(y4_to_y5)
            + list(y5_to_y6)
            + list(y6_to_y7)
            + list(y7_to_y8)
            + list(y8_to_y9)
            + list(y9_to_y10)
            + list(y10_to_y11)
            + list(y11_to_y11)
        )
        assert len(self.all_months_reductions) == 12 * 11

        month_cycle_starting_january = [
            JAN_KCALS_OG,
            FEB_KCALS_OG,
            MAR_KCALS_OG,
            APR_KCALS_OG,
            MAY_KCALS_OG,
            JUN_KCALS_OG,
            JUL_KCALS_OG,
            AUG_KCALS_OG,
            SEP_KCALS_OG,
            OCT_KCALS_OG,
            NOV_KCALS_OG,
            DEC_KCALS_OG
        ]

        # adjust cycle so it starts at the first month of the simulation
        self.months_cycle = month_cycle_starting_january[
            month_index:
        ] + month_cycle_starting_january[
            0:month_index
        ]

        self.KCALS_GROWN = []
        self.NO_ROT_KCALS_GROWN = []

        for i in range(0, self.NMONTHS):
            cycle_index = i % 12
            month_kcals = self.months_cycle[cycle_index]
            self.KCALS_GROWN.append(
                month_kcals
                * (
                    1
                    - (
                        self.OG_KCAL_REDUCED
                        * (1 - \
                            self.all_months_reductions[
                                i + month_index
                            ]
                        )
                    )
                )
            )
            self.NO_ROT_KCALS_GROWN.append(
                month_kcals
                * (
                    1
                    - (
                        (
                            1
                            - self.all_months_reductions[
                                i + month_index
                            ]
                        )
                    )
                )
            )

    def get_crop_production_minus_greenhouse_area(
        self, inputs_to_optimizer, greenhouse_fraction_area
    ):

        if self.ADD_OUTDOOR_GROWING:

            if inputs_to_optimizer["OG_USE_BETTER_ROTATION"]:

                crops_food_produced = np.array([0] * self.NMONTHS)

                hd = (
                    inputs_to_optimizer["INITIAL_HARVEST_DURATION_IN_MONTHS"]
                    + inputs_to_optimizer["DELAY"]["ROTATION_CHANGE_IN_MONTHS"]
                )

                crops_food_produced[hd:] = np.multiply(
                    np.array(self.KCALS_GROWN[hd:]), (1 - greenhouse_fraction_area[hd:])
                )

                crops_food_produced[:hd] = np.multiply(
                    np.array(self.NO_ROT_KCALS_GROWN[:hd]),
                    (1 - greenhouse_fraction_area[:hd]),
                )

            else:
                crops_food_produced = np.array(self.NO_ROT_KCALS_GROWN)

        else:
            crops_food_produced = np.array([0] * self.NMONTHS)

        return crops_food_produced
