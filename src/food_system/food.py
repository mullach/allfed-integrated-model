#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""

The idea here is that the code is constantly creating objects with calories, fat, and
protein separately then passing these objects around to other places, so we might as
well create a class which has these 3 properties.

Note that occasionally, this class is instantiated with each nutrient set as an array
where each element of the array is a different month of the simulation, and the total
number of months is NMONTHS, which is also the length of each of the 3 arrays.

TODO: comment on kcal inclusivness.

Created on Tue Jul 19

@author: morgan
"""
import numpy as np
import copy
from src.food_system.unit_conversions import UnitConversions
from src.utilities.plotter import Plotter


class Food(UnitConversions):
    """
    A food always has calories, fat, and protein.
    Food applies to biofuels and feed properties as well.

    A food always has units for each nutrient and these need to match when combining
    foods in some way, such as adding up, multiplying, or dividing their nutrients

    Best practice is to alter the food's units to be as specific as possible to prevent
    errors in the calculation.

    Here are some examples of using the food class:

    CONVENTIONS:
        A nutrient with a list of the value for each month, will need to
        have " each month" at the end of the units.
        A nutrient that represents the value for every month must have
        a " per month" at the end of the units.
        A nutrient with a single value all summed up over all time periods must not
        contain any " each month" or " per month" in the units.



    >>> example_food=Food(10,3,1)

    (defaults to billion kcals, thousand tons monthly fat, thousand tons monthly
    protein)

    >>> print(example_food):
        kcals: 10 billion kcals
        fat: 13  thousand tons
        protein: 1  thousand tons

    >>> example_food.set_units(
    >>>     kcals_units = 'ratio minimum global needs per year',
    >>>     fat_units = 'ratio minimum global needs per year',
    >>>     protein_units = 'ratio minimum global needs per year',
    >>> )
    >>> print(example_food):
        kcals: 10 ratio minimum global needs per year
        fat: 3  ratio minimum global needs per year
        protein: 1  ratio minimum global needs per year

    (in order to get a min nutrient, you need to make sure the units are all the same)
    (in reality, you would want to divide the values by the actual global needs above)

    >>> print(example_food.get_min_nutrient())
        ('protein', 1)

    >>> example_food_monthly = example_food / 12
    >>> example_food_monthly.set_units(
    >>>     kcals_units = 'ratio minimum global needs per month',
    >>>     fat_units = 'ratio minimum global needs per month',
    >>>     protein_units = 'ratio minimum global needs per month',
    >>> )

    >>> print(example_food_monthly)
        kcals: 0.8333333333333334 ratio minimum global needs per month
        fat: 0.25  ratio minimum global needs per month
        protein: 0.08333333333333333  ratio minimum global needs per month

    >>> NMONTHS = 3
    >>> example_food_all_months = Food(
    >>>     [example_food_monthly.kcals] * NMONTHS,
    >>>     [example_food_monthly.fat] * NMONTHS,
    >>>     [example_food_monthly.protein] * NMONTHS,
    >>> )
    >>> example_food_all_months.set_units(
    >>>     kcals_units = 'ratio minimum global needs each month',
    >>>     fat_units = 'ratio minimum global needs each month',
    >>>     protein_units = 'ratio minimum global needs each month',
    >>> )
    >>> print(example_food_all_months)
        kcals: [0.8333333333333334, 0.8333333333333334, 0.8333333333333334] ratio
        minimum global needs each month
        fat: [0.25, 0.25, 0.25]  ratio minimum global needs each month
        protein: [0.08333333333333333, 0.08333333333333333, 0.08333333333333333]
        ratio minimum global needs each month

    """

    # public property used to convert between units
    conversions = UnitConversions()

    @classmethod
    def get_Food_class(cls):
        """
        This function returns the class object of the current class.
        Args:
            cls (class): The class object of the current class.
        Returns:
            class: The class object of the current class.
        """
        return cls

    @classmethod
    def get_conversions(cls):
        """
        Returns the class conversions object.
        This method is only used by the parent UnitConversions class.

        Args:
            cls (class): The class object.

        Returns:
            conversions (object): The class conversions object.

        Raises:
            AssertionError: If the conversions property has not been assigned before
            attempting to convert between food units.
        """
        # Get the conversions object from the class
        conversions = cls.conversions
        # Check if the NUTRITION_PROPERTIES_ASSIGNED flag is True
        assert conversions.NUTRITION_PROPERTIES_ASSIGNED, """ERROR: you must
            assign the conversions property before attempting to convert between
            food units"""

        # Return the conversions object
        return conversions

    @classmethod
    def get_nutrient_names(cls):
        """
        Returns a list of the macronutrients of the food.

        Args:
            cls (class): The class object representing the Food class.

        Returns:
            list: A list of strings representing the macronutrients of the food.

        Example:
            >>> Food.get_nutrient_names()
            ['kcals', 'fat', 'protein']
        """
        # The macronutrients of the food
        return ["kcals", "fat", "protein"]

    @classmethod
    def ratio_one(cls):
        """
        Creates a Food object with kcals, fat, and protein all set to 1, and units set to "ratio".
        Returns:
            Food: a Food object with kcals, fat, and protein all set to 1, and units set to "ratio".
        """
        # Create a Food object with kcals, fat, and protein all set to 1, and units set to "ratio".
        return Food(
            kcals=1,
            fat=1,
            protein=1,
            # these are the default units but they can be overwritten
            kcals_units="ratio",
            fat_units="ratio",
            protein_units="ratio",
        )

    @classmethod
    def ratio_zero(cls):
        """
        Creates a Food object with all nutrient values set to 0 and units set to "ratio".
        Args:
            cls: the class object

        Returns:
            Food: a Food object with kcals, fat, and protein set to 0 and units set to "ratio".
        """

        return Food(
            kcals=0,
            fat=0,
            protein=0,
            # these are the default units but they can be overwritten
            kcals_units="ratio",
            fat_units="ratio",
            protein_units="ratio",
        )

    def __init__(
        # these are the default values but they can be overwritten
        self,
        kcals=0,
        fat=0,
        protein=0,
        # these are the default units but they can be overwritten
        kcals_units="billion kcals",
        fat_units="thousand tons",
        protein_units="thousand tons",
    ):
        """
        Initializes the food with the given macronutrients, and set the default units.
        """
        super().__init__()

        self.kcals = kcals
        self.fat = fat
        self.protein = protein

        self.set_units(
            kcals_units,
            fat_units,
            protein_units,
        )

        if self.is_list_monthly():
            self.NMONTHS = len(self.kcals)

            # np arrays are easier to work with than default python lists imho
            # TODO: make sure there's no way to sneakily directly define the .kcals etc
            #       as a default python list type and then get rid of all the casting to
            #       np arrays in the rest of the code
            self.kcals = np.array(self.kcals)

            # this is used to set a reasonable default if kcals are supplied but fat and
            # protein are not
            if "each month" not in self.kcals_units:
                self.kcals_units = self.kcals_units + " each month"

            if isinstance(self.fat, int):
                self.fat = np.zeros(len(self.kcals))
                self.fat_units = self.fat_units + " each month"
            else:
                self.fat = np.array(self.fat)

            if isinstance(self.protein, int):
                self.protein = np.zeros(len(self.kcals))
                self.protein_units = self.protein_units + " each month"
            else:
                self.protein = np.array(self.protein)

        else:
            self.NMONTHS = np.nan  # number of months is not a number

        self.validate_if_list()

    def new_food_just_from_kcals(
        # these are the default values but they can can be overwritten
        self,
        kcals=0,
        fat=0,
        protein=0,
        # these are the default units but they can be overwritten
        kcals_units="billion kcals",
        fat_units="thousand tons",
        protein_units="thousand tons",
    ):
        """
        Initializes a new food object with the given macronutrients and sets the default units.

        Args:
            kcals (float): The number of kilocalories in the food. Default is 0.
            fat (float): The amount of fat in the food. Default is 0.
            protein (float): The amount of protein in the food. Default is 0.
            kcals_units (str): The units for the kilocalories. Default is "billion kcals".
            fat_units (str): The units for the fat. Default is "thousand tons".
            protein_units (str): The units for the protein. Default is "thousand tons".

        Returns:
            None

        Example:
            >>> food = Food()
            >>> food.new_food_just_from_kcals(kcals=100, fat=10, protein=20)
        """

        # Call the parent constructor
        super().__init__()

        # Set the macronutrient values
        self.kcals = kcals
        self.fat = fat
        self.protein = protein

        # Set the units for the macronutrients
        self.set_units(
            kcals_units,
            fat_units,
            protein_units,
        )

        # Check if the food is a list of monthly values
        if self.is_list_monthly():
            # If it is, set the number of months and convert the macronutrient values to numpy arrays
            self.NMONTHS = len(self.kcals)

            # np arrays are easier to work with than default python lists imho
            # TODO: make sure there's no way to sneakily directly define the .kcals etc
            #       as a default python list type and then get rid of all the casting to
            #       np arrays in the rest of the code
            self.kcals = np.array(self.kcals)
            self.fat = np.array(self.fat)
            self.protein = np.array(self.protein)
        else:
            # If it's not a list of monthly values, set the number of months to NaN
            self.NMONTHS = np.nan

        # Validate the food object
        self.validate_if_list()

    # validation functions

    def total_energy_in_food(self):
        """
        Calculates the total energy in a given food in billion kcals by converting energy in protein and fat.
        Only works if:
        kcals_units="billion kcals",
        fat_units="thousand tons",
        protein_units="thousand tons",
        As a thousand tonnes, and a billion kcals are the same (10^9), the maths for conversion is simple.

        Args:
            self (Food): An instance of the Food class.

        Returns:
            float: The total energy in billion kcals.

        Raises:
            AssertionError: If kcals_units, fat_units, or protein_units are not set to the correct values.

        Example:
            >>> food = Food()
            >>> food.kcals_units = "billion kcals"
            >>> food.fat_units = "thousand tons"
            >>> food.protein_units = "thousand tons"
            >>> food.protein = 1000
            >>> food.fat = 2000
            >>> food.kcals = 3000
            >>> food.total_energy_in_food()
            23000.0
        """

        # Check that units are set correctly
        assert self.kcals_units == "billion kcals"
        assert self.fat_units == "thousand tons"
        assert self.protein_units == "thousand tons"

        # Define conversion factors
        protein_kcal = 4  # kcals per gram OR billion kcals per thousand tonnes
        fat_kcal = 9  # kcals per gram OR billion kcals per thousand tonnes

        # Calculate total energy in billion kcals
        total_energy_billion_kcals = (
            self.protein * protein_kcal
            + self.fat * fat_kcal  # billion kcals
            + self.kcals  # billion kcals
        )  # billion kcals

        return total_energy_billion_kcals

    def validate_if_list(self):
        """
        Checks if the food object is a list type and runs all the necessary checks to ensure
        that the list is properly set up.

        Args:
            self (Food): The Food object to be validated.

        Returns:
            None

        Example:
            >>> food = Food(name="Banana", kcals=[100, 120], fat=[0.3, 0.4], protein=[1.2, 1.5])
            >>> food.validate_if_list()
        """

        # Check if the food object is a list type
        if self.is_list_monthly():
            # Check if the units are set up correctly
            assert " each month" in self.kcals_units
            assert " each month" in self.fat_units
            assert " each month" in self.protein_units

            # Check if the list type food has the same number of months for all nutrients
            assert (
                len(self.kcals) == len(self.fat) == len(self.protein)
            ), "ERROR: list type food must have same number of months for all nutrients"

            # Check if the list type food has the same type of list for all nutrients
            assert isinstance(
                self.kcals, np.ndarray
            ), "ERROR: list type food must have same type of list for all nutrients"
            assert isinstance(
                self.fat, np.ndarray
            ), "ERROR: list type food must have same type of list for all nutrients"
            assert isinstance(
                self.protein, np.ndarray
            ), "ERROR: list type food must have same type of list for all nutrients"

            # Check if the list type food has more than one month
            assert (
                len(self.kcals) > 0
            ), "ERROR: list type food must have more than one month"

    def make_sure_not_a_list(self):
        """
        Check if any of the food nutrients are a list or numpy array and throw an error if so.
        Args:
            self: instance of the Food class
        Returns:
            None
        """
        # Check if kcals is a list or numpy array
        assert not isinstance(self.kcals, list) and not isinstance(
            self.kcals, np.ndarray
        )
        # Check if fat is a list or numpy array
        assert not isinstance(self.fat, list) and not isinstance(self.fat, np.ndarray)
        # Check if protein is a list or numpy array
        assert not isinstance(self.protein, list) and not isinstance(
            self.protein, np.ndarray
        )

    def make_sure_is_a_list(self):
        """
        This function checks if the food nutrients are in the form of a list and throws an error if not.
        It then validates the list properties.
        Args:
            self (Food): An instance of the Food class.
        Returns:
            None
        Example:
            >>> food = Food(kcals=[100, 200], fat=[5, 10], protein=[2, 4])
            >>> food.make_sure_is_a_list()
        """
        # Check if the food nutrients are in the form of a numpy array
        assert isinstance(self.kcals, np.ndarray)
        assert isinstance(self.fat, np.ndarray)
        assert isinstance(self.protein, np.ndarray)

    def make_sure_fat_protein_zero_if_kcals_is_zero(self):
        """
        This function ensures that the values of fat and protein are zero if kcals is zero.
        Args:
            self (Food): an instance of the Food class
        Returns:
            None
        """

        # Check if the list is monthly
        if self.is_list_monthly():
            # Validate the list
            self.validate_if_list()

            # Set the value of fat and protein to zero where kcals is zero
            fat_all_the_places_kcals_zero = np.where(
                self.kcals == 0,
                self.fat,
                0,
            )

            protein_all_the_places_kcals_zero = np.where(
                self.kcals == 0,
                self.protein,
                0,
            )

            # Check if fat and protein are zero where kcals is zero
            if self.conversions.include_fat:
                assert (fat_all_the_places_kcals_zero == 0).all()
            if self.conversions.include_protein:
                assert (protein_all_the_places_kcals_zero == 0).all()

        else:
            # Check if kcals is zero
            if self.kcals == 0:
                # Check if fat and protein are zero or excluded
                if self.conversions.include_fat:
                    assert self.fat == 0 or self.conversions.exclude_fat
                if self.conversions.include_protein:
                    assert self.protein == 0 or self.conversions.exclude_protein

    def ensure_other_list_zero_if_this_is_zero(self, other_list):
        """
        Get the value of the elements where the passed in list is zero, otherwise
        returned elements are zero.
        """
        self.make_sure_is_a_list()
        other_list.make_sure_is_a_list()

        assert other_list.NMONTHS == self.NMONTHS

        # values with zeros are zeros in all of our unit systems! How convenient.
        # That's why there's no need to check units.

        # here's an example of what np.where does in this context:
        #   >>> self = np.array([1005,693,0,532,786])   # random numbers
        #   >>> list_with_zeros = np.array([0,1,3,0,5]) # random numbers
        #   >>> replacement = np.array([101,62,23,3,0]) # random numbers
        #   >>>
        #   >>> # replace with the replacement if list_with_zeros is zero
        #   >>> processed_list = np.where(
        #   >>>     list_with_zeros == 0,
        #   >>>     replacement,
        #   >>>     self,
        #   >>> )
        #   >>>
        #   >>> print(processed_list)
        #   [101 693   0   3 786]

        # where self is nonzero, we don't care, so we set it to zero
        processed_list_kcals = np.where(
            self.kcals == 0,
            other_list.kcals,
            0,
        )

        if self.conversions.include_fat:
            processed_list_fat = np.where(
                self.fat == 0,
                other_list.fat,
                0,
            )
        else:
            processed_list_fat = np.zeros(len(processed_list_kcals))

        if self.conversions.include_protein:
            processed_list_protein = np.where(
                self.protein == 0,
                other_list.protein,
                0,
            )
        else:
            processed_list_protein = np.zeros(len(processed_list_kcals))

        processed_list = Food(
            kcals=processed_list_kcals,
            fat=processed_list_fat,
            protein=processed_list_protein,
            kcals_units=self.kcals_units,
            fat_units=self.fat_units,
            protein_units=self.protein_units,
        )

        assert processed_list.all_equals_zero()

    def make_sure_not_nan(self):
        """
        Check if the food's nutritional values are NaN and raise an assertion error if they are.
        Args:
            self (Food): An instance of the Food class.
        Returns:
            None
        """
        # Check if the food is a monthly list
        if self.is_list_monthly:
            # If it is, validate the list
            self.validate_if_list()
            # Check if any of the nutritional values are NaN and raise an assertion error if they are
            assert not np.isnan(self.kcals).any()
            assert not np.isnan(self.fat).any()
            assert not np.isnan(self.protein).any()
        else:
            # If it's not a monthly list, check if any of the nutritional values are NaN and raise an assertion error
            # if they are
            assert not np.isnan(self.kcals)
            assert not np.isnan(self.fat)
            assert not np.isnan(self.protein)

    # These are all for mathematical operations on the food's macronutrients, such as
    # adding, subtracting, multiplying, and dividing.

    def __add__(self, other):
        """
        Adds two foods together.

        Args:
            other (Food): The other food object to add to this one.

        Returns:
            Food: A new Food object with the sum of the kcals, fat, and protein of the two foods.

        Raises:
            AssertionError: If the units of the two foods are not the same.

        Example:
            >>> food1 = Food(100, 5, 10, "kcal", "g", "g")
            >>> food2 = Food(200, 10, 20, "kcal", "g", "g")
            >>> food3 = food1 + food2
            >>> food3.kcals
            300
            >>> food3.fat
            15
            >>> food3.protein
            30
        """
        assert (
            self.units == other.units
        )  # Check that the units of the two foods are the same

        # Add the kcals, fat, and protein of the two foods
        kcals = self.kcals + other.kcals
        fat = self.fat + other.fat
        protein = self.protein + other.protein

        # Create a new Food object with the sum of the kcals, fat, and protein of the two foods
        return Food(
            kcals, fat, protein, self.kcals_units, self.fat_units, self.protein_units
        )

    def __sub__(self, other):
        """
        Subtract two food nutrient quantities from each other.

        Args:
            other (Food): The other food object to subtract from self.

        Returns:
            Food: A new Food object with the nutrient quantities subtracted.

        Raises:
            AssertionError: If the units of the two Food objects are not the same.

        Example:
            >>> food1 = Food(100, 10, 20, "kcal", "g", "g")
            >>> food2 = Food(50, 5, 10, "kcal", "g", "g")
            >>> food3 = food1 - food2
            >>> food3.kcals
            50
            >>> food3.fat
            5
            >>> food3.protein
            10
        """
        assert self.units == other.units  # Check that the units are the same

        # Subtract the nutrient quantities
        kcals = self.kcals - other.kcals
        fat = self.fat - other.fat
        protein = self.protein - other.protein

        # Create a new Food object with the subtracted nutrient quantities
        return Food(
            kcals, fat, protein, self.kcals_units, self.fat_units, self.protein_units
        )

    def __truediv__(self, other):
        """
        Divides a food's macronutrients by a number.

        Args:
            other (Union[Food, float]): The food or number to divide by.

        Returns:
            Food: A new Food object with the divided macronutrient values.

        Raises:
            AssertionError: If the units of the two foods being divided are not the same.
            AssertionError: If both foods being divided are monthly lists, but the other is not.
            ValueError: If the other argument is a food list and this food is not a monthly list.

        Examples:
            >>> food1 = Food(100, 10, 20, "kcal", "g", "g")
            >>> food2 = Food(200, 20, 40, "kcal", "g", "g")
            >>> food3 = Food(50, 5, 10, "kcal", "g", "g")
            >>> food4 = Food(10, 1, 2, "kcal", "g", "g")
            >>> food_list1 = [food1, food2]
            >>> food_list2 = [food3, food4]
            >>> food1 / food2
            Food(0.5, 0.5, 0.5, 'ratio', 'ratio', 'ratio')
            >>> food_list1 / food_list2
            Food(2.0, 2.0, 2.0, 'ratio each month', 'ratio each month', 'ratio each month')
            >>> food1 / 2
            Food(50.0, 5.0, 10.0, 'kcal', 'g', 'g')

        """
        if isinstance(other, Food):
            # Check if the units of the two foods being divided are the same
            assert self.units == other.units

            if self.is_list_monthly():
                # Check if both foods being divided are monthly lists
                assert other.is_list_monthly(), """Error: for food lists, can
                    only divide by food lists at the moment. Consider implementing
                    additional cases."""

                # Validate if both foods are lists
                self.validate_if_list()
                other.validate_if_list()

                with np.errstate(divide="ignore"):
                    # ignoring divide by zero warnings
                    # (that's fine, divide by zero expected)
                    return Food(
                        np.divide(self.kcals, other.kcals),
                        np.divide(self.fat, other.fat),
                        np.divide(self.protein, other.protein),
                        "ratio each month",
                        "ratio each month",
                        "ratio each month",
                    )

            # Check if the other argument is a food list and this food is not a monthly list
            assert not other.is_list_monthly(), """Error: for foods, can only divide
                by foods or numbers at the moment, not food lists. Consider
                implementing additional cases."""

            return Food(
                self.kcals / other.kcals,
                self.fat / other.fat,
                self.protein / other.protein,
                "ratio",
                "ratio",
                "ratio",
            )
        else:
            kcals = self.kcals / other
            fat = self.fat / other
            protein = self.protein / other

            return Food(
                kcals,
                fat,
                protein,
                self.kcals_units,
                self.fat_units,
                self.protein_units,
            )

    def __getitem__(self, key):
        """
        Returns:
            A new Food object with the macronutrient values at the given index or range of indices.

        Args:
            key (int or slice): The index or range of indices to retrieve.

        NOTE:
            If key is a length 1 index, then this won't properly update units
            to " per month" and may cause an error down the line!

        TODO:
            Make sure this cannot happen by checking the length of key and updating units accordingly.

        This method retrieves the macronutrient values at the given index or range of indices and returns a new Food
        object with those values. It first ensures that the object's macronutrient values are in list form by calling
        the make_sure_is_a_list() method. It then validates that the list is of the same length for all macronutrients
        by calling the validate_if_list() method. Finally, it creates a new Food object with the macronutrient values
        at the given index or range of indices and returns it.

        Returns:
            A new Food object with the macronutrient values at the given index or range of indices.
        """
        self.make_sure_is_a_list()

        self.validate_if_list()

        return Food(
            kcals=self.kcals[key],
            fat=self.fat[key],
            protein=self.protein[key],
            kcals_units=self.kcals_units,
            fat_units=self.fat_units,
            protein_units=self.protein_units,
        )

    def __mul__(self, other):
        """
        Multiplies a food's macronutrients by a number.

        Args:
            other (typing.Union[Food, np.ndarray, float, int]): The object to multiply with the Food object.

        Returns:
            Food: A new Food object with the multiplied macronutrient values.

        This function multiplies a food's macronutrients by a number. The function can handle different types of
        inputs for the 'other' argument, including a Food object, a numpy array, a float,
        # or an int. The function returns a new Food object with the multiplied macronutrient values.

        The multiplication is constrained to handle only certain cases. The function can multiply ratios with
        non-ratios or ratios with ratios, because unit conversions can get confusing otherwise.

        There are many possibilities for the characteristics of the input values for self in other:

            - this is a food
            - this is a food list
            - other is a food
            - other is a food list
            - other is a non-food (like an int or a float)
            - other is a non-food numpy array (a type of list)

        which gives us the possible combinations:

            - this is a food and other is a food
            - this is a food and other is a food list
            - this is a food and other is non-food
            - this is a food list and other is a food
            - this is a food list and other is a food list
            - this is a food list and other is a non-food

        In addition, if other is a numpy array and this is not a food list, then we make this an "each month"
        food list.

        Units can be complicated when multiplying. If other is a non-food, there's no need to check units. Otherwise,
        the multiplication works right now only in the cases:

            - this is any units, other is a ratio
            - other is a ratio, this is any units
            - other is a ratio, this is a ratio

        """
        if not self.is_list_monthly():
            if isinstance(other, Food):
                # this is a food and other is a food
                if other.is_list_monthly():
                    # this is a food and other is a food list

                    this_is_the_ratio = self.is_a_ratio()

                    assert this_is_the_ratio, """unable to multiply a food by a food list
                     where the non-list food is not a ratio, consider implementing
                     this feature"""

                    kcals_units = other.kcals_units
                    fat_units = other.fat_units
                    protein_units = other.protein_units

                    return Food(
                        kcals=self.kcals * np.array(other.kcals),
                        fat=self.fat * np.array(other.fat),
                        protein=self.protein * np.array(other.protein),
                        kcals_units=kcals_units,
                        fat_units=fat_units,
                        protein_units=protein_units,
                    )

                this_is_the_ratio = self.is_a_ratio()
                other_is_the_ratio = other.is_a_ratio()

                assert (
                    this_is_the_ratio or other_is_the_ratio
                ), "list multiplication only works if one or both is a ratios right now"

                if this_is_the_ratio:
                    kcals_units = other.kcals_units
                    fat_units = other.fat_units
                    protein_units = other.protein_units

                if other_is_the_ratio:
                    kcals_units = self.kcals_units
                    fat_units = self.fat_units
                    protein_units = self.protein_units

                return Food(
                    self.kcals * other.kcals,
                    self.fat * other.fat,
                    self.protein * other.protein,
                    self.kcals_units,
                    self.fat_units,
                    self.protein_units,
                )

                assert self.get_units() == other.get_units_from_element_to_list()

            # this is a food and other is a list
            if isinstance(other, np.ndarray):
                # assume the other is unitless, we're converting a non-list food amount to a list
                # make this a food with "each month"
                return Food(
                    self.kcals * other,
                    self.fat * other,
                    self.protein * other,
                    self.kcals_units + " each month",
                    self.fat_units + " each month",
                    self.protein_units + " each month",
                )

            # this is a food and other is a non food

            return Food(
                self.kcals * other,
                self.fat * other,
                self.protein * other,
                self.kcals_units,
                self.fat_units,
                self.protein_units,
            )

        self.make_sure_is_a_list()
        self.validate_if_list()

        if isinstance(other, Food):
            if other.is_list_monthly():
                # this is a food list and other is a food list

                other.validate_if_list()

                this_is_the_ratio = self.is_a_ratio()
                other_is_the_ratio = other.is_a_ratio()

                assert (
                    this_is_the_ratio or other_is_the_ratio
                ), "list multiplication only works if one or both is a ratios right now"

                if this_is_the_ratio:
                    kcals_units = other.kcals_units
                    fat_units = other.fat_units
                    protein_units = other.protein_units

                if other_is_the_ratio:
                    kcals_units = self.kcals_units
                    fat_units = self.fat_units
                    protein_units = self.protein_units

                return Food(
                    kcals=np.multiply(np.array(self.kcals), np.array(other.kcals)),
                    fat=np.multiply(np.array(self.fat), np.array(other.fat)),
                    protein=np.multiply(
                        np.array(self.protein), np.array(other.protein)
                    ),
                    kcals_units=kcals_units,
                    fat_units=fat_units,
                    protein_units=protein_units,
                )

            # this is a food list and other is a food

            other_is_the_ratio = other.is_a_ratio()

            assert other_is_the_ratio, """unable to multiply a food list by a food
                where the non-list food is not a ratio, consider implementing
                this feature"""

            kcals_units = self.kcals_units
            fat_units = self.fat_units
            protein_units = self.protein_units

            return Food(
                kcals=self.kcals * other.kcals,
                fat=self.fat * other.fat,
                protein=self.protein * other.protein,
                kcals_units=kcals_units,
                fat_units=fat_units,
                protein_units=protein_units,
            )

        # this is a food list and other is a non food

        return Food(
            np.array(self.kcals) * other,
            np.array(self.fat) * other,
            np.array(self.protein) * other,
            self.kcals_units,
            self.fat_units,
            self.protein_units,
        )

    def __rmul__(self, other):
        """
        Multiplies a food's macronutrients by a number.
        This method is called when the argument is a number and the food object is on the right side of the operator.
        Args:
            other (int or float): The number to multiply the macronutrients by.
        Returns:
            Food: A new Food object with the macronutrients multiplied by the given number.
        """
        return self.__mul__(other)

    def __eq__(self, other):
        """
        Compares two Food objects for equality.

        Args:
            other (Food): The other Food object to compare to.

        Returns:
            bool: True if the two foods are equal. This also works
            for comparing monthly foods to each other, as their units
            contain 'each month'.

        Raises:
            AssertionError: If the units of the two foods are not equal.

        Example:
            >>> food1 = Food('apple', 50, 'g')
            >>> food2 = Food('apple', 50, 'g')
            >>> food1 == food2
            True
        """
        assert self.units == other.units  # Ensure units are equal
        if self.is_list_monthly():
            # Compare monthly foods
            return (
                (self.kcals == other.kcals).all()
                and (self.fat == other.fat).all()
                and (self.protein == other.protein).all()
            )
        else:
            # Compare non-monthly foods
            return (
                self.kcals == other.kcals
                and self.fat == other.fat
                and self.protein == other.protein
            )

    def __ne__(self, other):
        """
        Compares two Food objects and returns False if they are not equal.
        This also works for comparing monthly foods to each other, as their units
        contain 'each month'.

        Args:
            other (Food): The other Food object to compare to.

        Returns:
            bool: False if the two foods are not equal.

        Raises:
            AssertionError: If the units of the two foods are not the same.

        Example:
            >>> food1 = Food('apple', 100, 1, 1, 'each')
            >>> food2 = Food('banana', 100, 1, 1, 'each')
            >>> food1 != food2
            True
        """
        assert self.units == other.units  # Ensure the units are the same
        if self.is_list_monthly():
            # Compare monthly foods
            return (
                (self.kcals != other.kcals).any()
                or (self.fat != other.fat).any()
                or (self.protein != other.protein).any()
            )
        else:
            # Compare non-monthly foods
            return (
                self.kcals != other.kcals
                or self.fat != other.fat
                or self.protein != other.protein
            )

    def plot(self, title="generic food object over time"):
        """
        Plots the properties of this food object using the Plotter class.

        Args:
            title (str): The title of the plot. Defaults to "generic food object over time".

        Returns:
            str: The file path of the saved plot.

        Example:
            >>> food = Food()
            >>> food.plot("My Food Plot")
            '/path/to/saved/plot.png'
        """
        # Set a flag for alternative layout
        ALTERNATIVE_LAYOUT = False

        # Check if alternative layout is enabled
        if ALTERNATIVE_LAYOUT:
            # Use the alternative plotter method
            saveloc = Plotter.plot_food_alternative(self, title)
        else:
            # Use the default plotter method
            saveloc = Plotter.plot_food(self, title)

        # Return the file path of the saved plot
        return saveloc

    def __str__(self):
        """
        Returns:
            A string representation of the food, including its kcals, fat, and protein (if included).
        """
        # Initialize an empty string to hold the return value
        return_string = ""

        # Create a string representation of the kcals and add it to the return string
        kcal_string = "    kcals: % s % s" % (
            np.round(self.kcals, 5),
            self.kcals_units,
        )
        return_string = return_string + kcal_string

        # If fat is included, create a string representation of it and add it to the return string
        if self.conversions.include_fat:
            fat_string = "    fat: % s % s" % (np.round(self.fat, 5), self.fat_units)
            return_string = return_string + fat_string

        # If protein is included, create a string representation of it and add it to the return string
        if self.conversions.include_protein:
            protein_string = "    protein: % s % s" % (
                np.round(self.protein, 5),
                self.protein_units,
            )
            return_string = return_string + protein_string

        # Return the final string representation of the food
        return return_string

    def __neg__(self):
        """
        Returns a new Food object with negative nutrient values.

        Args:
            self (Food): The Food object to negate.

        Returns:
            Food: A new Food object with negative nutrient values.

        Example:
            >>> f = Food(kcals=100, fat=10, protein=5, kcals_units='kcal', fat_units='g', protein_units='g')
            >>> neg_f = -f
            >>> neg_f.kcals
            -100
            >>> neg_f.fat
            -10
            >>> neg_f.protein
            -5
            >>> neg_f.kcals_units
            'kcal'
            >>> neg_f.fat_units
            'g'
            >>> neg_f.protein_units
            'g'
        """
        return Food(
            kcals=-self.kcals,
            fat=-self.fat,
            protein=-self.protein,
            kcals_units=self.kcals_units,
            fat_units=self.fat_units,
            protein_units=self.protein_units,
        )

    def is_list_monthly(self):
        """
        Check if kcals is a list or numpy array.
        Args:
            self: instance of Food class
        Returns:
            bool: True if kcals is a list or numpy array, False otherwise
        """
        # Check if kcals is a list or numpy array
        return isinstance(self.kcals, list) or isinstance(self.kcals, np.ndarray)

    def is_never_negative(self):
        """
        Checks whether the food's macronutrients are never negative.

        Returns:
            bool: True if all macronutrients are non-negative, False otherwise.
        """
        # If the food is a list of monthly values, validate the list and check if all values are non-negative
        if self.is_list_monthly():
            self.validate_if_list()

            return (
                (np.array(self.kcals) >= 0).all()
                and ((np.array(self.fat) >= 0).all() or self.conversions.exclude_fat)
                and (
                    (np.array(self.protein) >= 0).all()
                    or self.conversions.exclude_protein
                )
            )
        # If the food is not a list, check if all macronutrients are non-negative
        return (
            self.kcals >= 0
            and (self.fat >= 0 or self.conversions.exclude_fat)
            and (self.protein >= 0 or self.conversions.exclude_protein)
        )

    def all_greater_than(self, other):
        """
        Determines if the macronutrient values of the current food object are greater than the macronutrient values of

        another food object.

        Args:
            other (Food): The other food object to compare against.

        Returns:
            bool: True if the current food object's macronutrient values are greater than the other food object's
            macronutrient values.

        Raises:
            AssertionError: If the units of the two food objects are not the same.

        Example:
            >>> food1 = Food('apple', 100, 0.3, 0.5, 0.2, 'g')
            >>> food2 = Food('banana', 120, 0.4, 0.6, 0.3, 'g')
            >>> food1.all_greater_than(food2)
            False
        """
        # Check if the units of the two food objects are the same
        assert self.units == other.units

        if self.is_list_monthly():
            # If the current food object is a monthly list, validate it
            self.validate_if_list()

            # Check if all macronutrient values of the current food object are greater than the other food object's
            # macronutrient values
            return (
                (np.array(self.kcals - other.kcals) > 0).all()
                and (
                    (np.array(self.fat - other.fat) > 0).all()
                    or self.conversions.exclude_fat
                )
                and (
                    (np.array(self.protein - other.protein) > 0).all()
                    or self.conversions.exclude_protein
                )
            )

        # Check if all macronutrient values of the current food object are greater than the other food object's
        # macronutrient values
        return (
            self.kcals > other.kcals
            and (self.fat > other.fat or self.conversions.exclude_fat)
            and (self.protein > other.protein or self.conversions.exclude_protein)
        )

    def all_less_than(self, other):
        """
        Compares the macronutrient values of two food items and returns True if the values of the current food item
        are less than the other food item's values.
        Args:
            other (Food): The other food item to compare with.

        Returns:
            bool: True if the current food item's macronutrient values are less than the other food item's values.

        Raises:
            AssertionError: If the units of the two food items are not the same.

        Example:
            >>> food1 = Food('apple', 50, 0.5, 0.1, 'g')
            >>> food2 = Food('banana', 100, 1.0, 0.2, 'g')
            >>> food1.all_less_than(food2)
            True
        """

        # Check if the units of the two food items are the same
        assert self.units == other.units

        if self.is_list_monthly():
            # If the current food item is a monthly list, validate it
            self.validate_if_list()

            # Compare the macronutrient values of the two food items using numpy arrays
            return (
                (np.array(self.kcals - other.kcals) < 0).all()
                and (
                    (np.array(self.fat - other.fat) < 0).all()
                    or self.conversions.exclude_fat
                )
                and (
                    (np.array(self.protein - other.protein) < 0).all()
                    or self.conversions.exclude_protein
                )
            )

        # Compare the macronutrient values of the two food items
        return (
            self.kcals < other.kcals
            and (self.fat < other.fat or self.conversions.exclude_fat)
            and (self.protein < other.protein or self.conversions.exclude_protein)
        )

    def any_greater_than(self, other):
        """
        Determines if the macronutrient values of the current food object are greater than the macronutrient values of
        another food object.

        Args:
            other (Food): The other food object to compare against.

        Returns:
            bool: True if the current food object's macronutrient values are greater than the other food object's
            macronutrient values.

        Raises:
            AssertionError: If the units of the two food objects are not the same.

        Example:
            >>> food1 = Food('apple', 95, 0.3, 0.5, 0.1, 'g')
            >>> food2 = Food('banana', 105, 0.4, 0.6, 0.1, 'g')
            >>> food1.any_greater_than(food2)
            False
        """

        # Ensure that the units of the two food objects are the same
        assert self.units == other.units

        # If the current food object is a list of monthly values, validate it
        if self.is_list_monthly():
            self.validate_if_list()

            # Check if any of the macronutrient values of the current food object are greater than the other food
            # object's
            return (
                (np.array(self.kcals - other.kcals) > 0).any()
                or (
                    (np.array(self.fat - other.fat) > 0).any()
                    and self.conversions.exclude_fat
                )
                or (
                    (np.array(self.protein - other.protein) > 0).any()
                    and self.conversions.exclude_protein
                )
            )

        # If the current food object is not a list of monthly values, compare the macronutrient values
        if self.conversions.include_fat:
            greater_than_fat = self.fat > other.fat
        else:
            greater_than_fat = False

        if self.conversions.include_protein:
            greater_than_protein = self.protein > other.protein
        else:
            greater_than_protein = False

        # Check if any of the macronutrient values of the current food object are greater than the other food object's
        return self.kcals > other.kcals or greater_than_fat or greater_than_protein

    def any_less_than(self, other):
        """
        Determines if the macronutrient values of the current food object are less than the macronutrient values of
        another food object.
        Args:
            other (Food): The other food object to compare against.
        Returns:
            bool: True if the current food object's macronutrient values are less than the other food object's
            macronutrient values.
        """

        # Ensure that the units of the two food objects are the same.
        assert self.units == other.units

        # If the current food object is a monthly list, validate it.
        if self.is_list_monthly():
            self.validate_if_list()

            # Check if any of the macronutrient values of the current food object are less than the other food
            # object's macronutrient values.
            return (
                (np.array(self.kcals - other.kcals) < 0).any()
                or (
                    (np.array(self.fat - other.fat) < 0).any()
                    and self.conversions.exclude_fat
                )
                or (
                    (np.array(self.protein - other.protein) < 0).any()
                    and self.conversions.exclude_protein
                )
            )

        # If the current food object is not a monthly list, compare the macronutrient values.
        if self.conversions.include_fat:
            less_than_fat = self.fat < other.fat
        else:
            less_than_fat = False

        if self.conversions.include_protein:
            less_than_protein = self.protein < other.protein
        else:
            less_than_protein = False

        # Check if the current food object's macronutrient values are less than the other food object's
        # macronutrient values.
        return self.kcals < other.kcals or less_than_fat or less_than_protein

    def all_greater_than_or_equal_to(self, other):
        """
        Compares the macronutrient values of two food items and returns True if the values of the
        current food item are greater than or equal to the other food item's values.

        Args:
            other (Food): The other food item to compare with.

        Returns:
            bool: True if the current food item's macronutrient values are greater than or equal to
            the other food item's values, False otherwise.
        """
        # Ensure that the units of the two food items are the same
        assert self.units == other.units

        if self.is_list_monthly():
            # If the current food item is a list of monthly values, validate it
            self.validate_if_list()

            # Compare the macronutrient values of the two food items using numpy arrays
            return (
                (np.array(self.kcals - other.kcals) >= 0).all()
                and (
                    (np.array(self.fat - other.fat) >= 0).all()
                    or self.conversions.exclude_fat
                )
                and (
                    (np.array(self.protein - other.protein) >= 0).all()
                    or self.conversions.exclude_protein
                )
            )

        # If the current food item is not a list of monthly values, compare the macronutrient
        # values directly
        return (
            self.kcals >= other.kcals
            and (self.fat >= other.fat or self.conversions.exclude_fat)
            and (self.protein >= other.protein or self.conversions.exclude_protein)
        )

    def all_less_than_or_equal_to(self, other):
        """
        Determines if the macronutrients of this food are less than or equal to the macronutrients of another food.
        Args:
            other (Food or List[Food]): The other food or list of foods to compare to.

        Returns:
            bool: True if the food's macronutrients are less than or equal to the other food's.

        Cases:
            - This is a single food, other is a single food
            - This is a single food, other is a list of foods
            - This is a list of foods, other is a single food
            - This is a list of foods, other is a list of foods
        """

        # Case 1: This is a single food, other is a single food
        if (not self.is_list_monthly()) and (not other.is_list_monthly()):
            assert self.units == other.units

            return (
                self.kcals <= other.kcals
                and (self.fat <= other.fat or self.conversions.exclude_fat)
                and (self.protein <= other.protein or self.conversions.exclude_protein)
            )

        # Case 2: This is a single food, other is a list of foods
        if (not self.is_list_monthly()) and other.is_list_monthly():
            assert self.get_units_from_element_to_list() == other.get_units()

        # Case 3: This is a list of foods, other is a single food
        if self.is_list_monthly() and not other.is_list_monthly():
            assert self.get_units() == other.get_units_from_element_to_list()

        # Case 4: This is a list of foods, other is a list of foods
        if (self.is_list_monthly()) and other.is_list_monthly():
            assert self.units == other.units

        return (
            (self.kcals <= other.kcals).all()
            and ((self.fat <= other.fat).all() or self.conversions.exclude_fat)
            and (
                (self.protein <= other.protein).all()
                or self.conversions.exclude_protein
            )
        )

    def any_greater_than_or_equal_to(self, other):
        """
        Determines if the macronutrient values of the current food object are greater than or equal to
        the macronutrient values of another food object.

        Args:
            other (Food): The other food object to compare against.

        Returns:
            bool: True if the current food object's macronutrient values are greater than or equal to
            the other food object's macronutrient values.
        """
        # Ensure that the units of the two food objects are the same.
        assert self.units == other.units

        # Check if the current food object is a monthly list.
        if self.is_list_monthly():
            # Validate the monthly list.
            self.validate_if_list()

            # Check if any of the macronutrient values of the current food object are greater than or equal to
            # the corresponding macronutrient values of the other food object.
            return (
                (np.array(self.kcals - other.kcals) >= 0).any()
                or (
                    (np.array(self.fat - other.fat) >= 0).any()
                    and self.conversions.exclude_fat
                )
                or (
                    (np.array(self.protein - other.protein) >= 0).any()
                    and self.conversions.exclude_protein
                )
            )

        # Check if any of the macronutrient values of the current food object are greater than or equal to
        # the corresponding macronutrient values of the other food object.
        return (
            self.kcals >= other.kcals
            or (self.fat >= other.fat and self.conversions.exclude_fat)
            or (self.protein >= other.protein and self.conversions.exclude_protein)
        )

    def any_less_than_or_equal_to(self, other):
        """
        Determines if the macronutrients of the current food object are less than or equal to
        those of another food object.

        Args:
            other (Food): The other food object to compare against.

        Returns:
            bool: True if the current food's macronutrients are less than or equal to the other food's.
        """

        # Check if the current food object is a monthly list
        if self.is_list_monthly():
            # Validate the list
            self.validate_if_list()

            # Check if fat is included in the conversions
            if self.conversions.include_fat:
                # Check if any of the fat values are less than or equal to the other food's fat values
                less_than_fat = (self.fat - other.fat <= 0).any()
            else:
                less_than_fat = False

            # Check if protein is included in the conversions
            if self.conversions.include_protein:
                # Check if any of the protein values are less than or equal to the other food's protein values
                less_than_protein = (self.protein - other.protein <= 0).any()
            else:
                less_than_protein = False

            # Check if any of the kcal values are less than or equal to the other food's kcal values,
            # or if any of the fat or protein values are less than or equal to the other food's fat or protein values
            return (
                (np.array(self.kcals - other.kcals) <= 0).any()
                or less_than_fat
                or less_than_protein
            )

        # If the current food object is not a monthly list, assert that the units are the same
        assert self.units == other.units

        # Check if fat is included in the conversions
        if self.conversions.include_fat:
            # Check if the current food's fat value is less than or equal to the other food's fat value
            less_than_fat = self.fat <= other.fat
        else:
            less_than_fat = False

        # Check if protein is included in the conversions
        if self.conversions.include_protein:
            # Check if the current food's protein value is less than or equal to the other food's protein value
            less_than_protein = self.protein <= other.protein
        else:
            less_than_protein = False

        # Check if the current food's kcal value is less than or equal to the other food's kcal value,
        # or if the current food's fat or protein value is less than or equal to the other food's fat or protein value
        return self.kcals <= other.kcals or less_than_fat or less_than_protein

    def all_equals_zero(self):
        """
        Check if all macronutrients of the food are equal to zero.
        Args:
            None
        Returns:
            bool: True if the food's macronutrients are equal to zero, False otherwise.
        """
        # Check if the food is monthly
        if self.is_list_monthly():
            # Validate the food list
            self.validate_if_list()

            # Check if all macronutrients are equal to zero
            return (
                (np.array(self.kcals) == 0).all()
                and ((np.array(self.fat) == 0).all() or self.conversions.exclude_fat)
                and (
                    (np.array(self.protein) == 0).all()
                    or self.conversions.exclude_protein
                )
            )

        # Check if all macronutrients are equal to zero
        return (
            self.kcals == 0
            and (self.fat == 0 or self.conversions.exclude_fat)
            and (self.protein == 0 or self.conversions.exclude_protein)
        )

    def any_equals_zero(self):
        """
        Check if any of the macronutrients of the food are equal to zero.
        Args:
            None
        Returns:
            bool: True if any of the macronutrients are equal to zero, False otherwise.
        """
        # Check if the food is a monthly list
        if self.is_list_monthly():
            # Validate the list
            self.validate_if_list()

            # Check if fat is included in the conversions
            if self.conversions.include_fat:
                zero_fat = (np.array(self.fat) == 0).any()
            else:
                zero_fat = False

            # Check if protein is included in the conversions
            if self.conversions.include_protein:
                zero_protein = (np.array(self.protein) == 0).any()
            else:
                zero_protein = False

            # Check if any of the kcals are equal to zero, or if fat or protein are equal to zero
            return (np.array(self.kcals) == 0).any() or zero_fat or zero_protein

        # If the food is not a monthly list
        if self.conversions.include_fat:
            zero_fat = self.fat == 0
        else:
            zero_fat = False

        if self.conversions.include_protein:
            zero_protein = self.protein == 0
        else:
            zero_protein = False

        # Check if any of the kcals are equal to zero, or if fat or protein are equal to zero
        return self.kcals == 0 or zero_fat or zero_protein

    def all_greater_than_zero(self):
        """
        Check if all macronutrients of the food are greater than zero.
        Args:
            None
        Returns:
            bool: True if all macronutrients are greater than zero, False otherwise.
        """
        # Check if the food is a list of monthly values
        if self.is_list_monthly():
            # Validate the list
            self.validate_if_list()

            # Check if all macronutrients are greater than zero using numpy's all() function
            return (
                (np.array(self.kcals) > 0).all()
                and (np.array(self.fat) > 0).all()
                and (np.array(self.protein) > 0).all()
            )

        # Check if all macronutrients are greater than zero
        return (
            self.kcals > 0
            and (self.fat > 0 or self.conversions.exclude_fat)
            and (self.protein > 0 or self.conversions.exclude_protein)
        )

    def any_greater_than_zero(self):
        """
        Returns True if any of the food's macronutrients are greater than zero.
        Args:
            self (Food): an instance of the Food class
        Returns:
            bool: True if any of the food's macronutrients are greater than zero, False otherwise
        """
        # Check if the food is a monthly list
        if self.is_list_monthly():
            # Validate the list
            self.validate_if_list()

            # Check if fat is included in the conversions
            if self.conversions.include_fat:
                zero_fat = (np.array(self.fat) > 0).any()
            else:
                zero_fat = False

            # Check if protein is included in the conversions
            if self.conversions.include_protein:
                zero_protein = (np.array(self.protein) > 0).any()
            else:
                zero_protein = False

            # Check if any of the kcals, fat, or protein are greater than zero
            return (np.array(self.kcals) > 0).any() or zero_fat or zero_protein

        # If the food is not a monthly list
        # Check if fat is included in the conversions
        if self.conversions.include_fat:
            zero_fat = self.fat > 0
        else:
            zero_fat = False

        # Check if protein is included in the conversions
        if self.conversions.include_protein:
            zero_protein = self.protein > 0
        else:
            zero_protein = False

        # Check if any of the kcals, fat, or protein are greater than zero
        return self.kcals > 0 or zero_fat or zero_protein

    def all_greater_than_or_equal_to_zero(self):
        """
        Checks if all macronutrients of the food are greater than or equal to zero.
        Args:
            self (Food): An instance of the Food class.
        Returns:
            bool: True if all macronutrients are greater than or equal to zero, False otherwise.
        """
        # Check if the food is monthly
        if self.is_list_monthly():
            # Validate the food list
            self.validate_if_list()

            # Check if all macronutrients are greater than or equal to zero
            return (
                (np.array(self.kcals) >= 0).all()
                and ((np.array(self.fat) >= 0).all() or self.conversions.exclude_fat)
                and (
                    (np.array(self.protein) >= 0).all()
                    or self.conversions.exclude_protein
                )
            )

        # Check if all macronutrients are greater than or equal to zero
        return (
            self.kcals >= 0
            and (self.fat >= 0 or self.conversions.exclude_fat)
            and (self.protein >= 0 or self.conversions.exclude_protein)
        )

    # Helper functions to get properties of the three nutrient values

    def as_numpy_array(self):
        """
        Returns:
            numpy.ndarray: an ordered numpy array containing the nutrients of the food.
        """
        # Create a numpy array with the kcals, fat, and protein values of the food
        return np.array([self.kcals, self.fat, self.protein])

    def get_min_nutrient(self):
        """
        Returns the minimum nutrient of the food.

        If the food is a list, it can return the minimum of any month of any nutrient.
        If the food is not a list, it returns the minimum of any nutrient.

        Only works when the units are identical for the different nutrients.

        Args:
            self: an instance of the Food class

        Returns:
            tuple: a tuple containing the name and value of the minimum nutrient

        Example:
            >>> food = Food()
            >>> food.get_min_nutrient()
            ('kcals', 0)

        Raises:
            AssertionError: if the units for kcals, fat, and protein are not identical
            AssertionError: if the minimum nutrient value is greater than the kcals value
            AssertionError: if the minimum nutrient value is greater than the fat value and
                            the fat nutrient is not excluded
            AssertionError: if the minimum nutrient value is greater than the protein value and
                            the protein nutrient is not excluded
        """
        assert self.kcals_units == self.fat_units == self.protein_units

        if self.is_list_monthly():
            to_find_min_of = self.get_min_all_months()
        else:
            to_find_min_of = self

        nutrients_dict = {}
        nutrients_dict["kcals"] = to_find_min_of.kcals

        if self.conversions.include_fat:
            nutrients_dict["fat"] = to_find_min_of.fat

        if self.conversions.include_protein:
            nutrients_dict["protein"] = to_find_min_of.protein

        # Using min() + list comprehension + values()
        # Finding min value keys in dictionary
        min_nutrient_val = min(nutrients_dict.values())
        min_nutrient_name = [
            key for key in nutrients_dict if nutrients_dict[key] == min_nutrient_val
        ][0]

        assert min_nutrient_val <= to_find_min_of.kcals
        # sometimes, this function causes an error for a single fat or protein
        # because the condition before the "or" is false, but doesn't find this for
        # the other because  the condition before the "or" is true
        assert min_nutrient_val <= to_find_min_of.fat or self.conversions.exclude_fat
        assert (
            min_nutrient_val <= to_find_min_of.protein
            or self.conversions.exclude_protein
        )

        return (min_nutrient_name, min_nutrient_val)

    def get_max_nutrient(self):
        """
        Returns the maximum nutrient of the food.

        NOTE:
            This function only works on single valued instances of nutrients, not arrays.

        Args:
            None

        Returns:
            tuple: A tuple containing the name and value of the maximum nutrient.

        Example:
            >>> food = Food()
            >>> food.kcals = 100
            >>> food.fat = 20
            >>> food.protein = 30
            >>> food.conversions.include_fat = True
            >>> food.conversions.include_protein = True
            >>> food.kcals_units = "kcal"
            >>> food.fat_units = "g"
            >>> food.protein_units = "g"
            >>> food.get_max_nutrient()
            ('fat', 20)

        """
        # Ensure that all nutrient units are the same
        assert self.kcals_units == self.fat_units == self.protein_units

        # Ensure that the food object is not a list
        self.make_sure_not_a_list()

        # Create a dictionary of nutrients and their values
        nutrients_dict = {}
        nutrients_dict["kcals"] = self.kcals

        if self.conversions.include_fat:
            nutrients_dict["fat"] = self.fat

        if self.conversions.include_protein:
            nutrients_dict["protein"] = self.protein

        # Using max() + list comprehension + values()
        # Finding max value keys in dictionary
        max_nutrient_val = max(nutrients_dict.values())
        max_key = [
            key for key in nutrients_dict if nutrients_dict[key] == max_nutrient_val
        ][0]

        # Ensure that the maximum nutrient value is greater than or equal to the kcals value
        assert max_nutrient_val >= self.kcals

        # Ensure that the maximum nutrient value is greater than or equal to the fat value, unless fat is excluded
        assert max_nutrient_val >= self.fat or self.conversions.exclude_fat

        # Ensure that the maximum nutrient value is greater than or equal to the protein value, unless protein is
        #  excluded
        assert max_nutrient_val >= self.protein or self.conversions.exclude_protein

        # Return the name and value of the maximum nutrient
        return (max_key, max_nutrient_val)

    def get_nutrients_sum(self):
        """
        Sums up the nutrients in all the months, then alters the units to remove "each month".
        Args:
            self: instance of the Food class
        Returns:
            Food: instance of the Food class with summed up nutrient values and altered units
        Raises:
            AssertionError: if the list is not monthly
        """
        # Check if the list is monthly
        assert self.is_list_monthly()

        # Validate the list
        self.validate_if_list()

        # Sum up the nutrient values
        food_sum = Food(
            sum(self.kcals),
            sum(self.fat),
            sum(self.protein),
            self.kcals_units,
            self.fat_units,
            self.protein_units,
        )

        # Alter the units to remove "each month"
        food_sum.set_units_from_list_to_total()

        # Return the summed up nutrient values with altered units
        return food_sum

    def get_running_total_nutrients_sum(self):
        """
        Calculates the running sum of the nutrients in all the months, without altering the units.
        Args:
            self: instance of the Food class
        Returns:
            Food: a new instance of the Food class with the running sum of the nutrients
        """
        # Check if the data is in monthly format
        assert self.is_list_monthly()

        # Create a deep copy of the kcals list
        kcals_copy = copy.deepcopy(self.kcals)
        running_sum_kcals = 0
        to_return_kcals = kcals_copy

        # Calculate the running sum of kcals for each month
        for i in range(self.NMONTHS):
            running_sum_kcals += kcals_copy[i]
            to_return_kcals[i] = running_sum_kcals

        # Create a deep copy of the fat list
        fat_copy = copy.deepcopy(self.fat)
        running_sum_fat = 0
        to_return_fat = fat_copy

        # Calculate the running sum of fat for each month
        for i in range(self.NMONTHS):
            running_sum_fat += fat_copy[i]
            to_return_fat[i] = running_sum_fat

        # Create a deep copy of the protein list
        protein_copy = copy.deepcopy(self.protein)
        running_sum_protein = 0
        to_return_protein = protein_copy

        # Calculate the running sum of protein for each month
        for i in range(self.NMONTHS):
            running_sum_protein += protein_copy[i]
            to_return_protein[i] = running_sum_protein

        # Validate if the data is in list format
        self.validate_if_list()

        # Return a new instance of the Food class with the running sum of the nutrients
        return Food(
            to_return_kcals,
            to_return_fat,
            to_return_protein,
            self.kcals_units,
            self.fat_units,
            self.protein_units,
        )

    def get_amount_used_other_food(self, other_fat_ratio, other_protein_ratio):
        """
        Running sum of the amount used of the other food each month.

        This function calculates the amount of stored food or outdoor growing that is
        used by biofuels and feed. It determines the amount of the other food used by
        taking the max amount used of the three nutrients, which is satisfied by a
        certain number of units of the other food. Surplus of the nutrients used is
        not used at all in the calculation.

        Args:
            other_fat_ratio (float): The ratio of fat in the other food
            other_protein_ratio (float): The ratio of protein in the other food

        Returns:
            Food: A Food object containing the amount of kcals, fat, and protein consumed
            each month

        Example:
            >>> food = Food(kcals=1000, fat=50, protein=30, kcals_units="kcal", fat_units="g", protein_units="g")
            >>> other_fat_ratio = 0.2
            >>> other_protein_ratio = 0.3
            >>> amount_consumed_list = food.get_amount_used_other_food(other_fat_ratio, other_protein_ratio)
        """

        # Ensure that the object is a list
        self.make_sure_is_a_list()

        # Validate the list
        self.validate_if_list()

        # Create a Food object with the ratio of fat and protein in the other food
        used_nutrient_ratio = Food(
            kcals=1,
            fat=other_fat_ratio,
            protein=other_protein_ratio,
            kcals_units="ratio",
            fat_units="ratio",
            protein_units="ratio",
        )

        # Create a Food object with zeros for kcals, fat, and protein for each month
        amount_consumed_list = Food(
            kcals=np.zeros(self.NMONTHS),
            fat=np.zeros(self.NMONTHS),
            protein=np.zeros(self.NMONTHS),
            kcals_units=self.kcals_units,
            fat_units=self.fat_units,
            protein_units=self.protein_units,
        )

        # Loop through each month and calculate the amount of the other food consumed
        for i in range(self.NMONTHS):
            demand_this_month = self.get_month(i)
            amount_consumed = self.get_consumed_amount(
                demand_this_month, used_nutrient_ratio
            )
            amount_consumed_list.kcals[i] = amount_consumed.kcals
            amount_consumed_list.fat[i] = amount_consumed.fat
            amount_consumed_list.protein[i] = amount_consumed.protein

        return amount_consumed_list

    def get_consumed_amount(self, demand_to_be_met, used_nutrient_ratio):
        """
        Returns the amount used of the demand_to_be_met a food with a given used_nutrient_ratio.
        The maximum nutrient used is used to determine the amount of the consumed
        food will be used.

        Args:
            demand_to_be_met (Food): A Food object representing the nutrient demand to be met
            used_nutrient_ratio (Food): A Food object representing the nutrient ratio of the food being consumed

        Returns:
            Food: A Food object representing the amount of food consumed to meet the nutrient demand

        Raises:
            AssertionError: If demand_to_be_met is a monthly list
            AssertionError: If used_nutrient_ratio fat or protein is less than or equal to 0
        """

        # Check if demand_to_be_met is not a monthly list
        assert not demand_to_be_met.is_list_monthly()

        # Check if used_nutrient_ratio fat and protein are greater than 0
        assert used_nutrient_ratio.fat > 0
        assert used_nutrient_ratio.protein > 0

        # Calculate the units of kcals, fat, and protein used to meet the nutrient demand
        kcals_units_used = demand_to_be_met.kcals
        fat_units_used = demand_to_be_met.fat / used_nutrient_ratio.fat
        protein_units_used = demand_to_be_met.protein / used_nutrient_ratio.protein

        # Determine the maximum units used to meet the nutrient demand
        max_units_used = max([kcals_units_used, fat_units_used, protein_units_used])

        # Return a Food object representing the amount of food consumed to meet the nutrient demand
        return Food(
            kcals=max_units_used * used_nutrient_ratio.kcals,
            fat=max_units_used * used_nutrient_ratio.fat,
            protein=max_units_used * used_nutrient_ratio.protein,
            kcals_units=demand_to_be_met.kcals_units,
            fat_units=demand_to_be_met.fat_units,
            protein_units=demand_to_be_met.protein_units,
        )

    def get_first_month(self):
        """
        Returns the nutrient values for the first month and converts the units from "each" to "per".
        Args:
            self: instance of the Food class
        Returns:
            dict: dictionary containing the nutrient values for the first month
        Raises:
            AssertionError: if the nutrient values are not in a list format
        """
        # Check if the nutrient values are in a list format
        assert self.is_list_monthly()

        # Return the nutrient values for the first month
        return self.get_month(0)

    def get_month(self, index):
        """
        Get the i month's nutrient values, and convert the units from "each" to "per".
        Args:
            index (int): The index of the month to retrieve nutrient values for.
        Returns:
            Food: A Food object containing the nutrient values for the specified month.
        """
        # Ensure that the list is monthly
        assert self.is_list_monthly()

        # Validate the list
        self.validate_if_list()

        # Create a new Food object with the nutrient values for the specified month
        food_at_month = Food(
            self.kcals[index],
            self.fat[index],
            self.protein[index],
            self.kcals_units,
            self.fat_units,
            self.protein_units,
        )

        # Convert the units from "each" to "per"
        food_at_month.set_units_from_list_to_element()

        # Return the Food object
        return food_at_month

    def get_min_all_months(self):
        """
        Creates a new Food object with the minimum nutrient values for each month.
        Args:
            self: The Food object to operate on.
        Returns:
            A new Food object with the minimum nutrient values for each month.
        """
        # Ensure that the object is a list
        self.make_sure_is_a_list()

        # Create a new Food object with the minimum nutrient values for each month
        min_all_months = Food(
            kcals=min(self.kcals),
            fat=min(self.fat),
            protein=min(self.protein),
            kcals_units=self.kcals_units,
            fat_units=self.fat_units,
            protein_units=self.protein_units,
        )

        # Set the units of the new object to be the same as the original object
        min_all_months.set_units_from_list_to_total()

        # Return the new object
        return min_all_months

    def get_max_all_months(self):
        """
        Returns a new Food object with the maximum nutrient values for each month.
        Args:
            self (Food): The Food object to find the maximum nutrient values for.
        Returns:
            Food: A new Food object with the maximum nutrient values for each month.
        """
        # Ensure that the object is a list
        self.make_sure_is_a_list()

        # Create a new Food object with the maximum nutrient values for each month
        max_all_months = Food(
            kcals=max(self.kcals),
            fat=max(self.fat),
            protein=max(self.protein),
            kcals_units=self.kcals_units,
            fat_units=self.fat_units,
            protein_units=self.protein_units,
        )

        # Set the units of the new Food object to total units
        max_all_months.set_units_from_list_to_total()

        # Return the new Food object
        return max_all_months

    def negative_values_to_zero(self):
        """
        Replaces negative values with zero for each month for all nutrients.
        If the food object is monthly, it replaces negative values for each month.
        If the food object is not monthly, it replaces negative values for the entire year.
        Also tests that the function worked by asserting that all values are greater than or equal to zero.

        Args:
            None

        Returns:
            Food: the relevant food object with negative values replaced
        """
        # Check if the food object is monthly
        if self.is_list_monthly():
            # Validate the food object
            self.validate_if_list()
            # Create a new food object with negative values replaced with zero
            zeroed_food = Food(
                kcals=np.where(self.kcals < 0, 0, self.kcals),
                fat=np.where(self.fat < 0, 0, self.fat),
                protein=np.where(self.protein < 0, 0, self.protein),
                kcals_units=self.kcals_units,
                fat_units=self.fat_units,
                protein_units=self.protein_units,
            )
        else:
            # Create a new food object with negative values replaced with zero
            zeroed_food = Food(
                kcals=0 if self.kcals < 0 else self.kcals,
                fat=0 if self.fat < 0 else self.fat,
                protein=0 if self.protein < 0 else self.protein,
                kcals_units=self.kcals_units,
                fat_units=self.fat_units,
                protein_units=self.protein_units,
            )

        # Assert that all values in the new food object are greater than or equal to zero
        assert zeroed_food.all_greater_than_or_equal_to_zero()

        # Return the new food object
        return zeroed_food

    def get_rounded_to_decimal(self, decimals):
        """
        Round the nutritional values of a food item to the nearest decimal place.

        Args:
            decimals (int): The number of decimal places to round to.

        Returns:
            Food: A new Food object with rounded nutritional values.

        Example:
            >>> food = Food(kcals=100.123, fat=5.678, protein=10.987, kcals_units='kcal',
            fat_units='g', protein_units='g')
            >>> rounded_food = food.get_rounded_to_decimal(1)
            >>> rounded_food.kcals
            100.1
            >>> rounded_food.fat
            5.7
            >>> rounded_food.protein
            11.0

        NOTE: This function is only implemented for lists at the moment.
        """

        # Make sure the food item is a list
        self.make_sure_is_a_list()

        # Round the nutritional values to the specified number of decimal places
        rounded = Food(
            kcals=np.round(self.kcals, decimals=decimals),
            fat=np.round(self.fat, decimals=decimals),
            protein=np.round(self.protein, decimals=decimals),
            kcals_units=self.kcals_units,
            fat_units=self.fat_units,
            protein_units=self.protein_units,
        )

        return rounded

    def replace_if_list_with_zeros_is_zero(self, list_with_zeros, replacement):
        """
        Replaces elements in a list with zeros with a specified replacement.

        Args:
            list_with_zeros (Food list): A list that has zeros in it.
            replacement (Food list, Food, or number): Thing used to replace the elements.

        Returns:
            Food: A copy of the original list with places where list_with_zeros is zero replaced with replacement.

        Raises:
            AssertionError: If the length of list_with_zeros is not equal to the length of the original list.
            AssertionError: If the units of replacement are not the same as the units of the original list.

        Example:
            >>> original_list = Food(kcals=[1005, 693, 0, 532, 786], fat=[10, 20, 0, 30, 40],
            protein=[5, 10, 0, 15, 20])
            >>> list_with_zeros = Food(kcals=[0, 1, 3, 0, 5], fat=[0, 1, 3, 0, 5], protein=[0, 1, 3, 0, 5])
            >>> replacement = Food(kcals=[101, 62, 23, 3, 0], fat=[1, 2, 3, 4, 5], protein=[10, 20, 30, 40, 50])
            >>> processed_list = original_list.replace_if_list_with_zeros_is_zero(list_with_zeros, replacement)
            >>> print(processed_list)
            kcals: [101 693   0   3 786], fat: [1 20 0 4 40], protein: [10 20 0 40 20]

        """
        # Ensure that both lists are actually lists
        self.make_sure_is_a_list()
        list_with_zeros.make_sure_is_a_list()

        # Ensure that the length of the list with zeros is equal to the length of the original list
        assert list_with_zeros.NMONTHS == self.NMONTHS

        # Ensure that the units of replacement are the same as the units of the original list
        if isinstance(replacement, Food):
            if replacement.is_list_monthly():
                assert self.NMONTHS == replacement.NMONTHS
                assert self.get_units() == replacement.get_units()
            else:
                assert self.get_units() == replacement.get_units_from_element_to_list()

        # Replace the elements in the list with zeros with the specified replacement
        if isinstance(replacement, Food):
            # Replacement specified per nutrient
            processed_list_kcals = np.where(
                list_with_zeros.kcals == 0,
                replacement.kcals,
                self.kcals,
            )

            processed_list_fat = np.where(
                list_with_zeros.fat == 0,
                replacement.fat,
                self.fat,
            )

            processed_list_protein = np.where(
                list_with_zeros.protein == 0,
                replacement.protein,
                self.protein,
            )
        else:
            # Replacement not specified per nutrient
            processed_list_kcals = np.where(
                list_with_zeros.kcals == 0,
                replacement,
                self.kcals,
            )

            processed_list_fat = np.where(
                list_with_zeros.fat == 0,
                replacement,
                self.fat,
            )

            processed_list_protein = np.where(
                list_with_zeros.protein == 0,
                replacement,
                self.protein,
            )

        # Create a new Food object with the processed list
        processed_list = Food(
            kcals=processed_list_kcals,
            fat=processed_list_fat,
            protein=processed_list_protein,
            kcals_units=self.kcals_units,
            fat_units=self.fat_units,
            protein_units=self.protein_units,
        )

        return processed_list

    def set_to_zero_after_month(self, month):
        """
        Set all values after the given month to zero.
        Args:
            month (int): The month after which all values should be set to zero.
        Returns:
            None
        """

        # Ensure that the object is a list
        self.make_sure_is_a_list()

        # Validate if the object is a list
        self.validate_if_list()

        # Set all values after the given month to zero
        self.kcals[month:] = 0
        self.fat[month:] = 0
        self.protein[month:] = 0
