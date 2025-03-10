
from idea_utils.PlateModel import Sample, Project, Plate


class WorkList():

    def __init__(self):
        self.records = []

    def selectTip(self, tip_index):
        self.records.append(f"S;{tip_index}")

    def addTransfer(self, asp, disp):
        self.addAspirateRecord(**asp)
        self.addDispenseRecord(**disp)
        self.addWashRecord()
        
    def addWashRecord(self):
        self.records.append("W;")

    def addAspirateRecord(self,
        rack_label="",
        rack_id="",
        rack_type="",
        position="",
        tube_id="",
        volume="",
        liquid_class="",
        # tip_type="",
        tip_mask="",
        forced_rack_type="",
        min_detected_volume=""):

        self.records.append(f"A;{rack_label};{rack_id};{rack_type};{position};{tube_id};{volume};{liquid_class};;{tip_mask};{forced_rack_type};{min_detected_volume}")

    def addDispenseRecord(self,
        rack_label="",
        rack_id="",
        rack_type="",
        position="",
        tube_id="",
        volume="",
        liquid_class="",
        # tip_type="",
        tip_mask="",
        forced_rack_type="",
        min_detected_volume=""):

        self.records.append(f"D;{rack_label};{rack_id};{rack_type};{position};{tube_id};{volume};{liquid_class};;{tip_mask};{forced_rack_type};{min_detected_volume}")

    def addReagentDistribution(self,
        src_rack_label="",
        src_rack_id="",
        src_rack_type="",
        src_start_pos="",
        src_end_pos="",
        dest_rack_label="",
        dest_rack_id="",
        dest_rack_type="",
        dest_start_pos="",
        dest_end_pos="",
        volume="",
        liquid_class="",
        diti_reuses="",
        multi_disp="",
        direction="",
        exclude=[]):

        self.records.append(f"R;{src_rack_label};{src_rack_id};{src_rack_type};{src_start_pos};{src_end_pos};{dest_rack_label};{dest_rack_id};{dest_rack_type};{dest_start_pos};{dest_end_pos};{volume};{liquid_class};{diti_reuses};{multi_disp};{direction};{";".join(str(e) for e in exclude)}")



    @classmethod
    def buildBCA(cls, sample_plates, dilutions):

        retval = WorkList()

        
        ### Add water to wells
        ####   Select tip and use reagent distribution records to save tips
        retval.selectTip(10)  ##  200ul tips
        bca_pos = 25

        


        ### Adding sample to wells
        bca_pos = 25
        retval.selectTip(12) ## 50ul tips
        for plate in sample_plates:
            for sample in plate.getSamples():
                vol = 100.0 / dilutions[sample.project.name].get()
                asp = {'rack_label':plate.name, 'rack_type':"IDeA 24 Eppendorf Tube", 'position':sample.position.index + 1, 'volume':vol, 'liquid_class':"Wet-NODET-50"}
                disp = {'rack_label':"BCA Plate", 'rack_type':"Falcon 96 Well Flat Bottom", 'position':bca_pos, 'volume':vol, 'liquid_class':"Wet-NODET-50"}
                retval.addTransfer(asp, disp)
                bca_pos += 1

        return retval



