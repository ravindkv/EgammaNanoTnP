import os
import sys
import json
sys.dont_write_bytecode = True
sys.path.insert(0, os.getcwd().replace("PlotHist", ""))
from PlotFunc import *
from Inputs import *
from PlotCMSLumi import *
from PlotTDRStyle import *
from ROOT import TFile, TLegend, gPad, gROOT, TCanvas, THStack, TF1, TH1F, TGraphAsymmErrors

padGap = 0.01
iPeriod = 4;
iPosX = 10;
ModTDRStyle()
xPadRange = [0.0,1.0]
yPadRange = [0.0,0.30-padGap, 0.30+padGap,1.0]

os.system("mkdir -p /eos/uscms/%s"%outPlotDir)

for var in xVars:
    gROOT.SetBatch(True)
    canvas = TCanvas()
    if len(forRatio)>0: 
        canvas.Divide(1, 2)
        canvas.cd(1)
        gPad.SetRightMargin(0.03);
        gPad.SetPad(xPadRange[0],yPadRange[2],xPadRange[1],yPadRange[3]);
        gPad.SetTopMargin(0.09);
        gPad.SetBottomMargin(padGap);
        #gPad.SetTickx(0);
        gPad.RedrawAxis();
        if("Pt") in var:
            gPad.SetLogx(True)
    else:
        canvas.cd()

    #get files
    files = {}
    for dirSamp in forOverlay:
        dirH = dirSamp.split("/")[0]
        samp = dirSamp.split("/")[1]
        inFile = TFile.Open("/eos/uscms/%s/%s/merged/%s_Hist.root"%(eosDir, dirH, samp))
        files["%s__%s"%(dirH, samp)] = inFile
        print(inFile)

    #get effs 
    effs = []
    for name, f in files.items(): 
        eff   = getEff(f, var, name)
        effs.append(eff)

    #plot effs
    leg = TLegend(0.25,0.85,0.95,0.92); 
    decoLegend(leg, 4, 0.027)
    for index, eff in enumerate(effs): 
        xTitle = var
        yTitle = "Efficiency"
        decoHist(eff, xTitle, yTitle, index+1)
        eff.SetMaximum(1.3)
        eff.SetMinimum(0.2)
        eff.GetXaxis().SetRangeUser(10, 400)
        if index==0:
            eff.Draw("AP")
        else:
            eff.Draw("Psame")
        leg.AddEntry(eff, "%s"%(eff.GetName().replace("HistNano_", "")), "APL")
        #leg.AddEntry(eff, "%s"%(eff.GetName()), "APL")
    
    #Draw CMS, Lumi, channel
    extraText  = "Preliminary"
    year = "XYZ"
    lumi_13TeV = getLumiLabel(year)
    CMS_lumi(lumi_13TeV, canvas, iPeriod, iPosX, extraText)
    leg.Draw()
    
    #Ratio lots
    if len(forRatio)>0: 
        canvas.cd(2)
        gPad.SetTopMargin(padGap); 
        gPad.SetBottomMargin(0.30); 
        gPad.SetRightMargin(0.03);
        if("Pt") in var:
            gPad.SetLogx(True)
        #gPad.SetTickx(0);
        gPad.SetPad(xPadRange[0],yPadRange[0],xPadRange[1],yPadRange[2]);
        gPad.RedrawAxis();
        rLeg = TLegend(0.25,0.75,0.95,0.85); 
        decoLegend(rLeg, 4, 0.085)
        baseLine = TF1("baseLine","1", -100, 10000);
        baseLine.SetLineColor(3);
        #baseLine.Draw()
        for index_, two in enumerate(forRatio):
            files = {}
            for dirSamp in two:
                dirH = dirSamp.split("/")[0]
                samp = dirSamp.split("/")[1]
                inFile = TFile.Open("/eos/uscms/%s/%s/merged/%s_Hist.root"%(eosDir, dirH, samp))
                files["%s__%s"%(dirH, samp)] = inFile
            hRatio = getRatio(files, var)
            decoHistRatio(hRatio, xTitle, "Ratio", index_+1)
            hRatio.GetYaxis().SetRangeUser(0.7, 1.3)
            hRatio.GetXaxis().SetRangeUser(10, 400)
            if index_==0:
                hRatio.Draw("AP")
            else:
                hRatio.Draw("Psame")
            rLeg.AddEntry(hRatio, "%s"%(hRatio.GetName()), "L")
        #rLeg.Draw()
    pdf = "/eos/uscms/%s/eff_%s.pdf"%(outPlotDir, var)
    png = pdf.replace("pdf", "png")
    canvas.SaveAs(pdf)
    canvas.SaveAs(png)
