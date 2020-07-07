from pathlib import Path
from snakemake.logging import logger
from snakemake.io import expand
from drop import utils

class AE:
    
    def __init__(self, config, sampleAnnotation, processedDataDir, processedResultsDir):
        self.processedDataDir = processedDataDir
        self.processedResultsDir = processedResultsDir
        self.sa = sampleAnnotation
        
        self.dict_ = self.setDefaultKeys(config["aberrantExpression"])
        self.groups = self.dict_["groups"]
        self.rnaIDs = self.sa.subsetGroups(self.groups, assay="RNA")
        
    
    def setDefaultKeys(self, dict_):
        setKey = utils.setKey
        dict_ = {} if dict_ is None else dict_
        
        setKey(dict_, None, "groups", self.sa.getGroups(assay="RNA"))
        setKey(dict_, None, "fpkmCutoff", 1)
        setKey(dict_, None, "implementation", "autoencoder")
        setKey(dict_, None, "padjCutoff", .05)
        setKey(dict_, None, "zScoreCutoff", 0)
        setKey(dict_, None, "maxTestedDimensionProportion", 3)
        
        return dict_

    def getCountFiles(self, annotation, group):
        ids = self.sa.getIDsByGroup(group, assay="RNA")
        file_stump = self.processedDataDir / "aberrant_expression" / annotation / "counts"
        return expand(str(file_stump) + "/{sampleID}.Rds", sampleID=ids)

        
class AS:
    
    def __init__(self, config, sampleAnnotation, processedDataDir, processedResultsDir):
        self.processedDataDir = processedDataDir
        self.processedResultsDir = processedResultsDir
        self.sa = sampleAnnotation
        
        self.dict_ = self.setDefaultKeys(config["aberrantSplicing"])
        self.groups = self.dict_["groups"]
        self.rnaIDs = self.sa.subsetGroups(self.groups, assay="RNA")
        
    
    def setDefaultKeys(self, dict_):
        setKey = utils.setKey
        dict_ = {} if dict_ is None else dict_
        
        setKey(dict_, None, "groups", self.sa.getGroups(assay="RNA"))
        setKey(dict_, None, "recount", False)
        setKey(dict_, None, "longRead", False)
        setKey(dict_, None, "filter", True)
        setKey(dict_, None, "minExpressionInOneSample", 20)
        setKey(dict_, None, "minDeltaPsi", 0)
        setKey(dict_, None, "implementation", "PCA")
        setKey(dict_, None, "padjCutoff", 0.05)
        setKey(dict_, None, "zScoreCutoff", 0.05)
        setKey(dict_, None, "deltaPsiCutoff", 0.05)
        setKey(dict_, None, "maxTestedDimensionProportion", 6)
        
        return dict_
        
    
class MAE:
    
    def __init__(self, config, sampleAnnotation, processedDataDir, processedResultsDir):
        self.processedDataDir = processedDataDir
        self.processedResultsDir = processedResultsDir
        self.sa = sampleAnnotation
        
        self.dict_ = self.setDefaultKeys(config["mae"])
        self.groups = self.dict_["groups"]
        self.qcGroups = self.dict_["qcGroups"]
        self.maeIDs = self.createMaeIDS(id_sep='--')
    
    def setDefaultKeys(self, dict_):
        setKey = utils.setKey
        dict_ = {} if dict_ is None else dict_
        
        groups = setKey(dict_, None, "groups", self.sa.getGroups(assay="DNA"))
        setKey(dict_, None, "qcGroups", groups)
        
        setKey(dict_, None, "gatkIgnoreHeaderCheck", True)
        setKey(dict_, None, "padjCutoff", .05)
        setKey(dict_, None, "allelicRatioCutoff", 0.8)
        setKey(dict_, None, "maxAF", .001)
        setKey(dict_, None, "gnomAD", False)
        
        return dict_
    
    def createMaeIDS(self, id_sep='--'):
        """
        Create MAE IDs from sample annotation
        """
        grouped_rna_ids = self.sa.subsetGroups(self.groups, assay="RNA", warn=1, error=1)
        id_map = self.sa.idMapping
        mae_ids = {}
        for gr, rna_ids in grouped_rna_ids.items():
            subset = id_map[id_map["RNA_ID"].isin(rna_ids)]
            dna_rna_pairs = zip(subset["DNA_ID"], subset["RNA_ID"])
            mae_ids[gr] = list(map(id_sep.join, dna_rna_pairs))
        return mae_ids
    
    def getMaeByGroup(self, group):
        if not isinstance(group, str):
            group = list(group)[0]
        return self.maeIDs[group]

    def getMaeAll(self):
        """
        Get a list of all MAE IDs from the groups specified in the config.
        Useful for collecting all MAE IDs ungrouped.
        """
        all_ids = []
        groups = [groups] if isinstance(self.groups, str) else self.groups
        for group in self.groups:
            all_ids.extend(self.getMaeByGroup(group))
        return all_ids