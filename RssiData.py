class RssiData:
    def __init__(self):
        self.device_whereabouts = [{}, {}]  # list of two dictionaries
        self.curr = 0  # index of the most updated dictionary of the two in the list - the one where you write to
        self.back = 1  # index of the second most up-to-date dictionary in the list - the one where you read from

    def Swap_Curr(self):
        """
        - makes the curr index, the back index
        """
        self.back = self.curr
        self.curr = (self.curr + 1) % 2

    def Get_Back(self):
        """
        - returns the dictionary in the self.back index
        - returns the dictionary that we want to read from (in order to get data for the gui)
        """
        back_dict = self.device_whereabouts[self.back]
        self.Swap_Curr()
        return back_dict
