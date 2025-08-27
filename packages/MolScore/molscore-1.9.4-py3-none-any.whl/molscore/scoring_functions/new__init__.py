import logging

logger = logging.getLogger(__name__)

class ScoringFunctions:
    _cache = {}
    _factories = {
        "MolecularDescriptors": "molscore.scoring_functions.descriptors",
        "RDKitDescriptors": "molscore.scoring_functions.descriptors",
        "LinkerDescriptors": "molscore.scoring_functions.descriptors",
        "MolSkill": "molscore.scoring_functions.molskill",
        "Isomer": "molscore.scoring_functions.isomer",
        "SillyBits": "molscore.scoring_functions.silly_bits",
        "MolecularSimilarity": "molscore.scoring_functions.similarity",
        "LevenshteinSimilarity": "molscore.scoring_functions.similarity",
        "TanimotoSimilarity": "molscore.scoring_functions.similarity",
        "ApplicabilityDomain": "molscore.scoring_functions.applicability_domain",
        "ChemistryFilter": "molscore.scoring_functions.chemistry_filters",
        "SubstructureFilters": "molscore.scoring_functions.substructure_filters",
        "SubstructureMatch": "molscore.scoring_functions.substructure_match",
        "BloomFilter": "molscore.scoring_functions.bloom_filter",
        "DecoratedReactionFilter": "molscore.scoring_functions.reaction_filter",
        "SelectiveDecoratedReactionFilter": "molscore.scoring_functions.reaction_filter",
        "RAScore_XGB": "molscore.scoring_functions.rascore_xgb",
        "AiZynthFinder": "molscore.scoring_functions.aizynthfinder",
        "PIDGIN": "molscore.scoring_functions.pidgin",
        "LegacyQSAR": "molscore.scoring_functions.legacy_qsar",
        "EnsembleSKLearnModel": "molscore.scoring_functions.sklearn_model",
        "SKLearnModel": "molscore.scoring_functions.sklearn_model",
        "ChemPropModel": "molscore.scoring_functions.chemprop",
        "ADMETAI": "molscore.scoring_functions.admet_ai",
        "Align3D": "molscore.scoring_functions.align3d", 
        "OEDock": "molscore.scoring_functions.oedock",
        "ROCS": "molscore.scoring_functions.rocs",
        "GlideDockFromROCS": "molscore.scoring_functions.rocs",  
        "GlideDock": "molscore.scoring_functions.glide",
        "PLANTSDock": "molscore.scoring_functions.plants",
        "ASPGOLDDock": "molscore.scoring_functions.gold",
        "ChemPLPGOLDDock": "molscore.scoring_functions.gold",
        "ChemScoreGOLDDock": "molscore.scoring_functions.gold",
        "GOLDDock": "molscore.scoring_functions.gold",
        "GoldScoreGOLDDock": "molscore.scoring_functions.gold",
        "rDock": "molscore.scoring_functions.rdock",
        "SminaDock": "molscore.scoring_functions.smina",
        "GninaDock": "molscore.scoring_functions.gnina",
        "VinaDock": "molscore.scoring_functions.vina",
        "POSTServer": "molscore.scoring_functions.external_server",
    #    "HSR": "molscore.scoring_functions.hsr", # Segmentation fault
    }
    
    @classmethod
    def get(cls, name, raise_errors=True):
        if name not in cls._cache:
            if name not in cls._factories:
                raise KeyError(f"No such function found: {name}")
            try:
                module_path = cls._factories[name]
                mod = __import__(module_path, fromlist=[""])
                cls._cache[name] = getattr(mod, name)
            except Exception as e:
                logger.warning(f"{name}: currently unavailable due to the following: {e}", exc_info=True)
                if raise_errors:
                    raise e
                else:
                    return None
        return cls._cache[name]
    
    @classmethod
    def get_all(cls):
        all_sfs = []
        for name in cls._factories:
            print(name)
            sf = cls.get(name, raise_errors=False)
            if sf is not None:
                all_sfs.append(sf)
        return all_sfs
    
    @classmethod
    def has(cls, name):
        return name in cls._factories
    
    @classmethod
    def get_names(cls):
        return list(cls._factories.keys())
