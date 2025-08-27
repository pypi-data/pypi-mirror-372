from copy import copy
from pydicom.tag import Tag
import pydicom
import itertools

def split_dynamics_to_series(input_list):
    """
    Splits a series containing multiple images per slice position (assumed to be multiple dynamics)
    into multiple series. DOES NOT MODIFY UIDs!

    This is not an intelligent function, and it assumes the images are already in some sort of
    sensible order... if this fails, it will need coding to also account for the acquisition timestamp.

    """

    # Check for repeated slice positions
    repeated_slice_positions,positions = check_repeated_positions(input_list,include_positions=True)
    if not repeated_slice_positions:
        print("No repeated positions detected")
        return None

    split_series = []
    positions_sorted = []

    for i in range(len(input_list)):
        if positions[i] in positions_sorted:
            # We've seen this position before
            j = positions_sorted.index(positions[i])
            split_series[j].append(input_list[i])
        else:
            # This is a new position
            positions_sorted.append(positions[i])
            split_series.append([])
            split_series[-1].append(input_list[i])
    
    # Currently have a list per slice position, we need to reshape this so that the top
    # level of the list is dynamic, not position

    split_series_reshaped = [list(a) for a in zip(*split_series)]
    
    # Split series is currently 

    print("SPLIT INTO {} SERIES".format(len(split_series_reshaped)))
    return split_series_reshaped



def check_repeated_positions(input_list,include_positions=False):
    """
    Takes an input list of pydicom Dataset objects and returns True if any slice positions are repeated.
    """
    positions = [(a.ImagePositionPatient,a.ImageOrientationPatient) for a in input_list]
    print(positions)
    checked_positions = []
    return_value = None
    for pos in positions:
        if not pos in checked_positions:
            checked_positions.append(pos)
        else:
            return_value = True
    if return_value is None:
        return_value = False
    if include_positions:
        return return_value,positions
    else:
        return return_value
