from loguru import logger

from phylodata.data_types import ClassificationEntry, DataType, Sample
from phylodata.errors import BlastError
from phylodata.process.samples.run_blast import extract_taxon_ids, run_blast
from phylodata.process.samples.taxon_classification import look_up_taxon_classification

MAX_SEQ_LENGTH_CONSIDERED = 2500


def add_nucleotide_metadata(samples: list[Sample]) -> list[Sample]:
    """Tries to add metadata to all samples for which we have nucleotide
    sequences."""
    # collect all nucleotide sequences

    nucleotide_sequences: list[str] = []
    nucleotide_sequence_idx: list[int] = []

    for idx, sample in enumerate(samples):
        if sample.classification:
            continue

        for data in sample.sample_data:
            if data.type in [DataType.RNA, DataType.DNA]:
                nucleotide_sequences.append(
                    "".join(c for c in data.data if c.isalpha())
                )
                nucleotide_sequence_idx.append(idx)

    # fetch the nucleotide classifications

    classification = fetch_nucleotide_classifications(nucleotide_sequences)

    # add the classifications to the samples

    for idx, classification in zip(nucleotide_sequence_idx, classification):
        if classification:
            samples[idx].classification = classification
            samples[idx].scientific_name = classification[0].scientific_name
            samples[idx].common_name = classification[0].common_name

    return samples


def fetch_nucleotide_classifications(
    sequences: list[str],
) -> list[list[ClassificationEntry] | None]:
    if not sequences:
        return []

    blast_params = {
        "CMD": "Put",
        "PROGRAM": "blastn",
        "MEGABLAST": True,
        "DATABASE": "core_nt",
        "HITLIST_SIZE": 1,
    }

    try:
        blast_results = run_blast(sequences, blast_params, MAX_SEQ_LENGTH_CONSIDERED)
    except BlastError:
        return [None] * len(sequences)

    taxon_ids = extract_taxon_ids(blast_results)

    classifications: list[list[ClassificationEntry] | None] = []

    for taxon_id in taxon_ids:
        if taxon_id:
            try:
                classifications.append(look_up_taxon_classification(taxon_id))
            except Exception as e:
                logger.error(f"Taxon look up faild: {e}")
                classifications.append(None)
        else:
            classifications.append(None)

    return classifications
