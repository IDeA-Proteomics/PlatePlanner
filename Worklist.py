
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

    def addBreakRecord(self):
        self.records.append("B;")

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
    def buildBCA(cls, plates, dilutions):

        retval = WorkList()

        
        ### Add water to wells
        ####   Select tip and use reagent distribution records to save tips

        dil_amounts = {d for d in dilutions.values()}

        for d in dil_amounts:
            sam_pos = {s.position.index + 1 for s in plates[0].getSamples() if s.project.name != "Standards" and dilutions[s.project.name] == d}
            sam_pos = sorted(sam_pos)
            first = sam_pos[0]
            last = sam_pos[-1]
            volume = 100.0 - (100.0 / d)
            exclude = [i for i in range(first, last) if i not in sam_pos]

            retval.addBreakRecord()
            retval.selectTip(10)

            retval.addReagentDistribution(src_rack_label="Water", src_rack_type="Trough 100ml", src_start_pos='1', src_end_pos='8', 
                                          dest_rack_label="BCA Plate", dest_rack_type="Falcon 96 Well Flat Bottom", dest_start_pos=str(first), dest_end_pos=str(last),
                                          volume=volume, liquid_class="IDeA NODET", diti_reuses='99', exclude=exclude)       
        
        retval.addWashRecord()
        retval.addBreakRecord()


        ### Adding sample to wells
        retval.selectTip(12) ## 50ul tips

        for sample in plates[0].getSamples():
            if sample.project.name == "Standards":
                continue
            volume = 100.0 / dilutions[sample.project.name]

            samp_plate = None
            samp_pos = None
            ###  Find sample in sample plates
            found = False
            for p in plates[1:]:
                for s in p.getSamples():
                    if s.name == sample.name:
                        samp_plate = p
                        samp_pos = str(s.position.index + 1)
                        found = True
                        break
                if found:
                    break

            if samp_plate is not None and samp_pos is not None:
                asp = {'rack_label':samp_plate.name, 'rack_type':"IDeA 24 Eppendorf Tube", 'position':samp_pos, 'volume':volume, 'liquid_class':"Wet-NODET-50"}
                disp = {'rack_label':"BCA Plate", 'rack_type':"Falcon 96 Well Flat Bottom", 'position':sample.position.index + 1, 'volume':volume, 'liquid_class':"Wet-NODET-50"}
                retval.addTransfer(asp, disp)


        


        # for plate in plates:
        #     for sample in plate.getSamples():
        #         vol = 100.0 / dilutions[sample.project.name].get()
        #         asp = {'rack_label':plate.name, 'rack_type':"IDeA 24 Eppendorf Tube", 'position':sample.position.index + 1, 'volume':vol, 'liquid_class':"Wet-NODET-50"}
        #         disp = {'rack_label':"BCA Plate", 'rack_type':"Falcon 96 Well Flat Bottom", 'position':bca_pos, 'volume':vol, 'liquid_class':"Wet-NODET-50"}
        #         retval.addTransfer(asp, disp)
        #         bca_pos += 1

        return retval



