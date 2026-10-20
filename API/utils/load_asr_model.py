from omegaconf import OmegaConf, DictConfig
import nemo.collections.asr as nemo_asr
import torch

def load_asr_model():
    asr_model = nemo_asr.models.EncDecHybridRNNTCTCBPEModel.from_pretrained(
        model_name="nvidia/stt_pl_fastconformer_hybrid_large_pc"
    )
    device = "cuda" if torch.cuda.is_available() else "cpu"
    asr_model.to(device)

    OmegaConf.set_struct(asr_model.cfg.aux_ctc.decoding, False)
    asr_model.cfg.aux_ctc.decoding.preserve_alignments = True
    asr_model.cfg.aux_ctc.decoding.compute_timestamps = True
    asr_model.cfg.aux_ctc.decoding.confidence_cfg = DictConfig({
        "preserve_frame_confidence": True,
        "preserve_token_confidence": True,
        "preserve_word_confidence": True,
        "exclude_blank": True,
        "aggregation": "mean",
        "method_cfg": {
            "name": "entropy",
            "entropy_type": "tsallis",
            "alpha": 0.33,
            "entropy_norm": "exp",
        }
    })
    OmegaConf.set_struct(asr_model.cfg.aux_ctc.decoding, True)
    asr_model.change_decoding_strategy(asr_model.cfg.aux_ctc.decoding, decoder_type="ctc")

    return asr_model