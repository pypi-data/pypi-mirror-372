from vtk import vtkThreshold


def get_threshold_between(input_source, lower_bound, upper_bound, field_association, field_name, idx=0, port=0,
                          connection=0, source_is_input_connection=0, invert=False):
    """

    :param input_source: Input data to threshold. Can be either an input connection or input data format.
    Set source_is_input_connection to 1 if it's an input connection. Automatically swaps variables if lower_bound > upper_bound.
    :param lower_bound:
    :param upper_bound:
    :param field_association: Type of field
    :param field_name:
    :param idx: further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param port:further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param connection:further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param source_is_input_connection: 1 if it's an input connection, 0 if it's an input data format
    :param invert: True if selection should be inverted
    :return: initialized and updated threshold object
    :return:
    """
    if lower_bound > upper_bound:
        # switch variables
        lower_bound, upper_bound = upper_bound, lower_bound

    thresh = vtkThreshold()
    thresh.SetThresholdFunction(vtkThreshold.THRESHOLD_BETWEEN)

    if source_is_input_connection:
        thresh.SetInputConnection(input_source)
    else:
        thresh.SetInputData(input_source)
    thresh.SetLowerThreshold(lower_bound)
    thresh.SetUpperThreshold(upper_bound)
    if invert:
        thresh.InvertOn()
    thresh.SetInputArrayToProcess(idx, port, connection, field_association, field_name)
    thresh.Update()
    return thresh


def get_lower_threshold(input_source, lower_bound, field_association, field_name, idx=0, port=0,
                        connection=0, source_is_input_connection=0):
    """
    Encapsulates vtk lower threshold

    :param input_source: Input data to threshold. Can be either an input connection or input data format.
    Set source_is_input_connection to 1 if it's an input connection
    :param lower_bound: lower bound for filtering the input source
    :param field_association: Type of field
    :param field_name:
    :param idx: further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param port:further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param connection:further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param source_is_input_connection: 1 if it's an input connection, 0 if it's an input data format
    :return: initialized and updated threshold object
    """

    thresh = vtkThreshold()

    if source_is_input_connection:
        thresh.SetInputConnection(input_source)
    else:
        thresh.SetInputData(input_source)

    return _standard_thresholding(thresh, vtkThreshold.THRESHOLD_LOWER, lower_bound, field_association, field_name,
                                  idx, port, connection)


def get_upper_threshold(input_source, upper_bound, field_association, field_name, idx=0, port=0, connection=0,
                        source_is_input_connection=0):
    """
    Encapsulates vtk lower threshold

    :param input_source: Input data to threshold. Can be either an input connection or input data format.
    Set source_is_input_connection to 1 if it's an input connection
    :param upper_bound: lower bound for filtering the input source
    :param field_association: Type of field
    :param field_name:
    :param idx: further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param port:further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param connection:further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param source_is_input_connection: 1 if it's an input connection, 0 if it's an input data format
    :return: initialized and updated threshold object
    """

    thresh = vtkThreshold()
    if source_is_input_connection:
        thresh.SetInputConnection(input_source)
    else:
        thresh.SetInputData(input_source)

    return _standard_thresholding(thresh, vtkThreshold.THRESHOLD_UPPER, upper_bound, field_association, field_name,
                                  idx, port, connection)


def _standard_thresholding(thresh, thresh_function, bound_value, field_association, field_name, idx=0, port=0,
                           connection=0):
    """
    Thresholding generator for lower and upper threshold.
    Should not be used outside these script, for thresholding use get_upper/lower_threshold functions
    :param thresh: Initialized thresh object
    :param thresh_function: vtkThreshold.THRESHOLD_LOWER or vtkThreshold.THRESHOLD_UPPER
    :param bound_value: upper or lower bound value
    :param field_association: Type of field
    :param field_name:
    :param idx: further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param port:further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :param connection:further details see vtk.vtkThreshold.SetInputArrayToProcess()
    :return: Initialized and updated threshold object
    """
    thresh.SetThresholdFunction(thresh_function)
    if thresh_function is vtkThreshold.THRESHOLD_LOWER:
        thresh.SetLowerThreshold(bound_value)
    elif thresh_function is vtkThreshold.THRESHOLD_UPPER:
        thresh.SetUpperThreshold(bound_value)
    else:
        raise ValueError(f"Threshold function {thresh_function} is not supported ")

    thresh.SetInputArrayToProcess(idx, port, connection, field_association, field_name)

    thresh.Update()
    return thresh
