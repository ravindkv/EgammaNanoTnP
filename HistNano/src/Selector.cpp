#include"Selector.h"

Selector::Selector(){
}

std::vector<int> Selector::filter_electrons(EventTree *tree){
    std::vector<int> selEles_;
    for(int eleInd = 0; eleInd < tree->nEle; ++eleInd){
        double eta = tree->eleEta[eleInd];
        double absEta = TMath::Abs(eta);
        double SCeta = eta + tree->eleDeltaEtaSC[eleInd];
        double absSCEta = TMath::Abs(SCeta);
        double pt = tree->elePt[eleInd];
        // make sure it doesn't fall within the gap
        bool passEtaEBEEGap = (absSCEta < 1.4442) || (absSCEta > 1.566);

        Int_t eleID = tree->eleID[eleInd];
        bool passVetoID  = (eleID==1); 
        bool passTightID = (eleID==4);

        bool eleSel = (passEtaEBEEGap && 
                       absEta <= 2.4 &&
                       pt >= 32.0 &&
                       passTightID);
        if(eleSel) selEles_.push_back(eleInd);
    }
    return selEles_;
}


bool Selector::filter_Z(EventTree *tree, vector<int> selEles__){
    bool passZ = true;
    if(selEles__.size() == 2) {
		int idx_ele1 = selEles__.at(0);
		int idx_ele2 = selEles__.at(1);
		if((tree->eleCharge[idx_ele1])*(tree->eleCharge[idx_ele2]) == 1){
		    passZ = false;
		}
		TLorentzVector ele1;
		TLorentzVector ele2;
		ele1.SetPtEtaPhiM(tree->elePt[idx_ele1],
			  tree->eleEta[idx_ele1],
			  tree->elePhi[idx_ele1],
			  tree->eleMass[idx_ele1]);
		ele2.SetPtEtaPhiM(tree->elePt[idx_ele2],
			  tree->eleEta[idx_ele2],
			  tree->elePhi[idx_ele2],
			  tree->eleMass[idx_ele2]);
		if ( abs((ele1 + ele2).M() - 91.1876) > 30 ){
		    passZ = false;
		}
    }
    else { 
        passZ = false;
    }
    return passZ;
}

bool Selector::isTrigMatched(EventTree *tree, int ind){
    bool isMatch=false;
    for(int j=0;j<tree->nTrigObj;j++){
        double dR = deltaR(tree->eleEta[ind],  tree->elePhi[ind], tree->TrigObj_eta[j], tree->TrigObj_phi[j]);
        // filterbit 2 is for hltEle32WPTightGsfTrackIsoFilter (of HLT_ELe32_WPTight_Gsf) 
        //std::cout<<dR<<", "<<tree->TrigObj_pt[j]<<", "<<abs(tree->TrigObj_id[j])<<", "<<tree->TrigObj_filterBits[j]<<std::endl;
        if(dR <0.1 && tree->TrigObj_pt[j]>32 && abs(tree->TrigObj_id[j])==11  && (tree->TrigObj_filterBits[j] & 2)==2) isMatch = true; 
    }
    return isMatch;
}


Selector::~Selector(){
}