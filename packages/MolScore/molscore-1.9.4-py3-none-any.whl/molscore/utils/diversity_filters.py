import abc
from collections import Counter

from rdkit import Chem, rdBase
from rdkit.Chem.Scaffolds import MurckoScaffold

from molscore.utils import transformation_functions as tfuncs

rdBase.DisableLog("rdApp.error")


class DivBuffer:
    def __init__(self):
        """Diversity buffer, instead of storing everything, we'll only store centroid information, member indexes otherwise."""
        self.memory = []  ## List of dictionaries {centroid: str, scaffold: str, fp: rdkit.FP, members: list}
        self.centroids = []

    def add(self, smiles, scores=None):
        if scores:
            assert len(smiles) == len(
                scores
            ), "Score vector is not the same length as SMILES list"
        scaffolds = [self.getScaffold(smi) for smi in smiles]
        self._update_memory(smiles, scaffolds, scores)
        return scaffolds

    def addGeneric(self, smiles, scores=None):
        if scores:
            assert len(smiles) == len(
                scores
            ), "Score vector is not the same length as SMILES list"
        scaffolds = [self.getGenericScaffold(smi) for smi in smiles]
        self._update_memory(smiles, scaffolds, scores)
        return scaffolds

    def getScaffold(self, smile):
        mol = Chem.MolFromSmiles(smile)
        if mol:
            scaffold = MurckoScaffold.GetScaffoldForMol(mol)
            return Chem.MolToSmiles(scaffold, isomericSmiles=False)
        else:
            return ""

    def getGenericScaffold(self, smile):
        mol = Chem.MolFromSmiles(smile)
        if mol:
            scaffold = MurckoScaffold.MakeScaffoldGeneric(
                MurckoScaffold.GetScaffoldForMol(mol)
            )
            return Chem.MolToSmiles(scaffold, isomericSmiles=False)
        else:
            return ""

    def _update_memory(self, smiles, scaffolds, scores=None, fingerprints=None):
        for i, smi in enumerate(smiles):
            scaffold = scaffolds[i]
            if fingerprints is not None:
                self._morganfp[scaffold] = fingerprints[i]
            score = scores[i]
            if scaffold in self._scaffolds:
                self._scaffolds[scaffold][smi] = score
            else:
                self._scaffolds[scaffold] = {smi: score}

    def has(self, scaffold, smiles):
        if scaffold in self._scaffolds:
            if smiles in self._scaffolds[scaffold]:
                return True
        return False

    def getFingerprints(self):
        return self._morganfp

    def __getitem__(self, scaffold):
        if scaffold in self._scaffolds:
            return self._scaffolds[scaffold]
        else:
            return []


class DivFilter(DivBuffer):
    def __init__(self):
        super().__init__()
        self.index = 0

    @abc.abstractmethod
    def score(self, smiles, scores) -> dict:
        """
        Logic:
        - Convert SMILES to relevant similarity representation
        - Check SMILES against buffer
        - If present:
            - Add to member list
            - Calculate score
        - If not present:
            - Add to buffer as new centroid
            - Calculate score
        - Return [{DF_score, DF_passes, DF_centroid, DF_cluster_idx, DF_cluster_size}]
        """
        raise NotImplementedError


class Unique(DivFilter):
    def __init__(self, minscore=0.5):
        super().__init__()
        self.centroids = set()  # Override
        self.min_score = minscore

    def score(self, smiles, scores):
        results = []
        for smi, sc in zip(smiles, scores):
            if (smi in self.centroids) and (sc >= self.min_score):
                results.append(
                    {
                        "DF_score": 0,
                        "DF_passes": False,
                        "DF_centroid": False,
                        "DF_cluster_idx": None,
                        "DF_cluster_size": None,
                    }
                )
            else:
                if sc >= self.min_score:
                    self.centroids.add(smi)
                results.append(
                    {
                        "DF_score": sc,
                        "DF_passes": True,
                        "DF_centroid": True,
                        "DF_cluster_idx": None,
                        "DF_cluster_size": None,
                    }
                )
        return results


class Occurrence(DivFilter):
    def __init__(self, minscore=0.5, tolerance=1, buffer=1):
        super().__init__()
        self.centroids = Counter()  # Override
        self.minscore = minscore
        self.tolerance = tolerance
        self.buffer = buffer

    def score(self, smiles, scores):
        results = []
        for smi, sc in zip(smiles, scores):
            if (smi in self.centroids) and (sc >= self.minscore):
                # Update
                self.centroids.update([smi])
                # Penalize
                pen_sc = self.penalize_score(sc, self.centroids[smi])
                results.append(
                    {
                        "DF_score": pen_sc,
                        "DF_passes": pen_sc == sc,
                        "DF_centroid": False,
                        "DF_cluster_idx": None,
                        "DF_cluster_size": self.centroids[smi],
                    }
                )
            else:
                # Update
                if sc >= self.minscore:
                    self.centroids.update([smi])
                # Don't penalize
                results.append(
                    {
                        "DF_score": sc,
                        "DF_passes": True,
                        "DF_centroid": True,
                        "DF_cluster_idx": None,
                        "DF_cluster_size": 1,
                    }
                )
        return results

    def penalize_score(self, sc, occs):
        pen_sc = sc * tfuncs.lin_thresh(
            x=occs,
            objective="minimize",
            upper=0,
            lower=self.tolerance,
            buffer=self.buffer,
        )
        return pen_sc


class ScaffoldMatcher(DivFilter):
    def __init__(self, nbmax=25, minscore=0.6, generic=False, outputmode="binary"):
        super().__init__()
        self.centroids = set()  # Override
        self.nbmax = nbmax
        self.minscore = minscore
        self.generic = generic
        self.outputmode = outputmode

    def score(self, smiles, scores):
        results = []
        for smi, sc in zip(smiles, scores):
            scaff = self.getScaffold(smi, generic=self.generic)
            if (scaff in self.centroids) and (sc >= self.minscore):
                results.append(
                    {
                        "DF_score": 0,
                        "DF_passes": False,
                        "DF_centroid": False,
                        "DF_cluster_idx": None,
                        "DF_cluster_size": None,
                    }
                )
            else:
                if sc >= self.minscore:
                    self.add([smi])
                results.append(
                    {
                        "DF_score": sc,
                        "DF_passes": True,
                        "DF_centroid": True,
                        "DF_cluster_idx": None,
                        "DF_cluster_size": None,
                    }
                )


class IdenticalMurckoScaffold(ScaffoldMatcher):
    """Penalizes compounds based on exact Murcko Scaffolds previously generated. 'minsimilarity' is ignored."""

    def __init__(self, nbmax=25, minscore=0.6, outputmode="binary", **kwargs):
        """
        :param nbmax: Maximum number of molecules per memory bin (cluster)
        :param minscore: Minimum molecule score required to consider for memory binning
        :param outputmode: 'binary' (1 or 0), 'linear' (1 - fraction of bin) or 'sigmoid' (1 - sigmoid(fraction of bin)) [binary, linear, sigmoid]
        :param kwargs:
        """
        super().__init__(nbmax=nbmax, minscore=minscore, generic=False, outputmode=outputmode)


class IdenticalTopologicalScaffold(ScaffoldMatcher):
    """Penalizes compounds based on exact Topological Scaffolds previously generated. 'minsimilarity' is ignored."""

    def __init__(self, nbmax=25, minscore=0.6, outputmode="binary", **kwargs):
        """
        :param nbmax: Maximum number of molecules per memory bin (cluster)
        :param minscore: Minimum molecule score required to consider for memory binning
        :param outputmode: 'binary' (1 or 0), 'linear' (1 - fraction of bin) or 'sigmoid' (1 - sigmoid(fraction of bin)) [binary, linear, sigmoid]
        :param kwargs:
        """
        super().__init__(nbmax=nbmax, minscore=minscore, generic=True, outputmode=outputmode)
