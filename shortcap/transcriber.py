import logging
import numpy as np
from typing import Optional
from .config import (
    MODEL,
    DEVICE,
    COMPUTE_TYPE,
    BATCH_SIZE
)

# 获取 logger
logger = logging.getLogger("shortcap.transcriber")


class TranscriptionError(Exception):
    """Custom exception class for handling errors during transcription"""

    pass


def transcribe_locally(audio_file: str, align_words: bool, language: Optional[str]):
    """
    Transcribe an audio file using the whisperx package
    (https://github.com/m-bain/whisperX)
    """

    try:
        import whisperx
    except ImportError:
        logger.error("Unable to import whisperx module. Make sure whisperx is installed.")
        raise TranscriptionError("Unable to import whisperx module. Make sure whisperx is installed.")

    try:
        logger.info("Loading Whisper model")
        model = whisperx.load_model(MODEL, DEVICE, compute_type=COMPUTE_TYPE)
    except Exception as e:
        logger.error(f"Error loading Whisper model: {str(e)}")
        raise TranscriptionError(f"Failed to load Whisper model: {str(e)}")

    try:
        logger.info("Starting local transcription")
        result = model.transcribe(audio_file, batch_size=BATCH_SIZE,language=language)
        logger.info("Local transcription completed successfully")
    except Exception as e:
        logger.error(f"Error during local transcription: {str(e)}")
        raise TranscriptionError(f"Local transcription failed: {str(e)}")

    language_found = result["language"]

    if align_words:
        try:
            logger.info("Starting alignment")
            model_a, metadata = whisperx.load_align_model(language_code=language_found, device=DEVICE)
            result = whisperx.align(result["segments"], model_a, metadata, audio_file, DEVICE, return_char_alignments=False)
            logger.info("Alignment completed successfully")
        except Exception as e:
            logger.error(f"Error during local transcription: {str(e)}")
            raise TranscriptionError(f"Local transcription failed: {str(e)}")
    
    return result["segments"], language_found

    """
    anyme = [{'start': 2.44, 'end': 2.902, 'text': ' Oh non.', 'words': [{'word': 'Oh', 'start': np.float64(2.44), 'end': np.float64(2.721), 'score': np.float64(0.428)}, {'word': 'non.', 'start': np.float64(2.781), 'end': np.float64(2.902), 'score': np.float64(0.343)}]}, {'start': 2.942, 'end': 6.514, 'text': 'Et donc on est sur un jeune RS6 de coiffeur frérot.', 'words': [{'word': 'Et', 'start': np.float64(2.942), 'end': np.float64(3.002), 'score': np.float64(0.462)}, {'word': 'donc', 'start': np.float64(3.022), 'end': np.float64(3.143), 'score': np.float64(0.294)}, {'word': 'on', 'start': np.float64(3.243), 'end': np.float64(3.303), 'score': np.float64(0.592)}, {'word': 'est', 'start': np.float64(3.363), 'end': np.float64(3.484), 'score': np.float64(0.457)}, {'word': 'sur', 'start': np.float64(3.524), 'end': np.float64(3.624), 'score': np.float64(0.627)}, {'word': 'un', 'start': np.float64(3.704), 'end': np.float64(3.865), 'score': np.float64(0.52)}, {'word': 'jeune', 'start': np.float64(3.885), 'end': np.float64(4.266), 'score': np.float64(0.603)}, {'word': 'RS6', 'start': np.float64(4.306), 'end': np.float64(5.109), 'score': np.float64(0.862)}, {'word': 'de', 'start': np.float64(5.149), 'end': np.float64(5.711), 'score': np.float64(0.731)}, {'word': 'coiffeur', 'start': np.float64(5.731), 'end': np.float64(6.132), 'score': np.float64(0.65)}, {'word': 'frérot.', 'start': np.float64(6.193), 'end': np.float64(6.514), 'score': np.float64(0.71)}]}, {'start': 6.574, 'end': 11.189, 'text': 'Un jeune RS6 mytho frérot.', 'words': [{'word': 'Un', 'start': np.float64(6.574), 'end': np.float64(6.674), 'score': np.float64(0.806)}, {'word': 'jeune', 'start': np.float64(6.694), 'end': np.float64(6.955), 'score': np.float64(0.634)}, {'word': 'RS6', 'start': np.float64(6.975), 'end': np.float64(7.677), 'score': np.float64(0.808)}, {'word': 'mytho', 'start': np.float64(7.697), 'end': np.float64(8.079), 'score': np.float64(0.762)}, {'word': 'frérot.', 'start': np.float64(8.099), 'end': np.float64(11.189), 'score': np.float64(0.464)}]}, {'start': 11.229, 'end': 11.831, 'text': 'Je suis mort.', 'words': [{'word': 'Je', 'start': np.float64(11.229), 'end': np.float64(11.329), 'score': np.float64(0.57)}, {'word': 'suis', 'start': np.float64(11.349), 'end': np.float64(11.49), 'score': np.float64(0.54)}, {'word': 'mort.', 'start': np.float64(11.53), 'end': np.float64(11.831), 'score': np.float64(0.831)}]}, {'start': 11.851, 'end': 12.272, 'text': 'Bon attends.', 'words': [{'word': 'Bon', 'start': np.float64(11.851), 'end': np.float64(11.951), 'score': np.float64(0.421)}, {'word': 'attends.', 'start': np.float64(11.992), 'end': np.float64(12.272), 'score': np.float64(0.582)}]}, {'start': 12.313, 'end': 13.316, 'text': "Ah mais du coup j'ai cassé ma tête.", 'words': [{'word': 'Ah', 'start': np.float64(12.313), 'end': np.float64(12.353), 'score': np.float64(0.026)}, {'word': 'mais', 'start': np.float64(12.373), 'end': np.float64(12.453), 'score': np.float64(0.503)}, {'word': 'du', 'start': np.float64(12.493), 'end': np.float64(12.533), 'score': np.float64(0.004)}, {'word': 'coup', 'start': np.float64(12.553), 'end': np.float64(12.634), 'score': np.float64(0.714)}, {'word': "j'ai", 'start': np.float64(12.654), 'end': np.float64(12.734), 'score': np.float64(0.176)}, {'word': 'cassé', 'start': np.float64(12.754), 'end': np.float64(12.995), 'score': np.float64(0.285)}, {'word': 'ma', 'start': np.float64(13.015), 'end': np.float64(13.075), 'score': np.float64(0.93)}, {'word': 'tête.', 'start': np.float64(13.115), 'end': np.float64(13.316), 'score': np.float64(0.813)}]}, {'start': 13.336, 'end': 13.617, 'text': 'Attends.', 'words': [{'word': 'Attends.', 'start': np.float64(13.336), 'end': np.float64(13.617), 'score': np.float64(0.713)}]}, {'start': 13.657, 'end': 14.761, 'text': "Oh non j'ai cassé ma tête les gars.", 'words': [{'word': 'Oh', 'start': np.float64(13.657), 'end': np.float64(13.717), 'score': np.float64(0.242)}, {'word': 'non', 'start': np.float64(13.737), 'end': np.float64(13.838), 'score': np.float64(0.373)}, {'word': "j'ai", 'start': np.float64(13.858), 'end': np.float64(14.078), 'score': np.float64(0.516)}, {'word': 'cassé', 'start': np.float64(14.098), 'end': np.float64(14.239), 'score': np.float64(0.329)}, {'word': 'ma', 'start': np.float64(14.259), 'end': np.float64(14.319), 'score': np.float64(0.861)}, {'word': 'tête', 'start': np.float64(14.359), 'end': np.float64(14.52), 'score': np.float64(0.802)}, {'word': 'les', 'start': np.float64(14.56), 'end': np.float64(14.62), 'score': np.float64(0.311)}, {'word': 'gars.', 'start': np.float64(14.64), 'end': np.float64(14.761), 'score': np.float64(0.392)}]}]

    return anyme, "fr"
    """

    """
    palma = [
        {
            "start": 9.363,
            "end": 12.267,
            "text": " Bonjour.",
            "words": [
                {
                    "word": "Bonjour.",
                    "start": np.float64(9.363),
                    "end": np.float64(12.267),
                    "score": np.float64(0.638),
                }
            ],
        },
        {
            "start": 12.287,
            "end": 14.209,
            "text": "Parlez-moi un peu de votre expérience terroriste.",
            "words": [
                {
                    "word": "Parlez-moi",
                    "start": np.float64(12.287),
                    "end": np.float64(12.607),
                    "score": np.float64(0.763),
                },
                {
                    "word": "un",
                    "start": np.float64(12.627),
                    "end": np.float64(12.667),
                    "score": np.float64(0.096),
                },
                {
                    "word": "peu",
                    "start": np.float64(12.687),
                    "end": np.float64(12.787),
                    "score": np.float64(0.784),
                },
                {
                    "word": "de",
                    "start": np.float64(12.807),
                    "end": np.float64(12.867),
                    "score": np.float64(0.753),
                },
                {
                    "word": "votre",
                    "start": np.float64(12.887),
                    "end": np.float64(13.027),
                    "score": np.float64(0.84),
                },
                {
                    "word": "expérience",
                    "start": np.float64(13.047),
                    "end": np.float64(13.428),
                    "score": np.float64(0.936),
                },
                {
                    "word": "terroriste.",
                    "start": np.float64(13.448),
                    "end": np.float64(14.209),
                    "score": np.float64(0.847),
                },
            ],
        },
        {
            "start": 14.289,
            "end": 17.433,
            "text": "Alors, j'ai été kamikaze pendant trois ans.",
            "words": [
                {
                    "word": "Alors,",
                    "start": np.float64(14.289),
                    "end": np.float64(14.87),
                    "score": np.float64(0.577),
                },
                {
                    "word": "j'ai",
                    "start": np.float64(14.97),
                    "end": np.float64(15.07),
                    "score": np.float64(0.597),
                },
                {
                    "word": "été",
                    "start": np.float64(15.11),
                    "end": np.float64(15.27),
                    "score": np.float64(0.839),
                },
                {
                    "word": "kamikaze",
                    "start": np.float64(15.31),
                    "end": np.float64(15.771),
                    "score": np.float64(0.652),
                },
                {
                    "word": "pendant",
                    "start": np.float64(15.791),
                    "end": np.float64(16.011),
                    "score": np.float64(0.577),
                },
                {
                    "word": "trois",
                    "start": np.float64(16.051),
                    "end": np.float64(16.231),
                    "score": np.float64(0.766),
                },
                {
                    "word": "ans.",
                    "start": np.float64(16.271),
                    "end": np.float64(17.433),
                    "score": np.float64(0.821),
                },
            ],
        },
        {
            "start": 17.473,
            "end": 19.375,
            "text": "Ça va bien.",
            "words": [
                {
                    "word": "Ça",
                    "start": np.float64(17.473),
                    "end": np.float64(17.573),
                    "score": np.float64(0.452),
                },
                {
                    "word": "va",
                    "start": np.float64(17.593),
                    "end": np.float64(17.713),
                    "score": np.float64(0.336),
                },
                {
                    "word": "bien.",
                    "start": np.float64(17.753),
                    "end": np.float64(19.375),
                    "score": np.float64(0.881),
                },
            ],
        },
        {
            "start": 19.435,
            "end": 22.739,
            "text": "Et puis j'ai piloté un avion le 11 septembre aussi.",
            "words": [
                {
                    "word": "Et",
                    "start": np.float64(19.435),
                    "end": np.float64(19.495),
                    "score": np.float64(0.362),
                },
                {
                    "word": "puis",
                    "start": np.float64(19.515),
                    "end": np.float64(20.056),
                    "score": np.float64(0.75),
                },
                {
                    "word": "j'ai",
                    "start": np.float64(20.096),
                    "end": np.float64(20.236),
                    "score": np.float64(0.934),
                },
                {
                    "word": "piloté",
                    "start": np.float64(20.276),
                    "end": np.float64(20.677),
                    "score": np.float64(0.741),
                },
                {
                    "word": "un",
                    "start": np.float64(20.697),
                    "end": np.float64(20.777),
                    "score": np.float64(0.342),
                },
                {
                    "word": "avion",
                    "start": np.float64(20.817),
                    "end": np.float64(21.037),
                    "score": np.float64(0.875),
                },
                {
                    "word": "le",
                    "start": np.float64(21.077),
                    "end": np.float64(21.337),
                    "score": np.float64(0.448),
                },
                {"word": "11"},
                {
                    "word": "septembre",
                    "start": np.float64(21.378),
                    "end": np.float64(21.718),
                    "score": np.float64(0.852),
                },
                {
                    "word": "aussi.",
                    "start": np.float64(21.758),
                    "end": np.float64(22.739),
                    "score": np.float64(0.38),
                },
            ],
        },
        {
            "start": 22.879,
            "end": 23.42,
            "text": "Ah oui, d'accord.",
            "words": [
                {
                    "word": "Ah",
                    "start": np.float64(22.879),
                    "end": np.float64(22.939),
                    "score": np.float64(0.212),
                },
                {
                    "word": "oui,",
                    "start": np.float64(22.959),
                    "end": np.float64(23.12),
                    "score": np.float64(0.302),
                },
                {
                    "word": "d'accord.",
                    "start": np.float64(23.16),
                    "end": np.float64(23.42),
                    "score": np.float64(0.626),
                },
            ],
        },
        {
            "start": 23.44,
            "end": 24.802,
            "text": "Je ne suis pas le genre de kamikaze.",
            "words": [
                {
                    "word": "Je",
                    "start": np.float64(23.44),
                    "end": np.float64(23.5),
                    "score": np.float64(0.245),
                },
                {
                    "word": "ne",
                    "start": np.float64(23.52),
                    "end": np.float64(23.56),
                    "score": np.float64(0.003),
                },
                {
                    "word": "suis",
                    "start": np.float64(23.6),
                    "end": np.float64(23.7),
                    "score": np.float64(0.127),
                },
                {
                    "word": "pas",
                    "start": np.float64(23.72),
                    "end": np.float64(23.861),
                    "score": np.float64(0.331),
                },
                {
                    "word": "le",
                    "start": np.float64(23.881),
                    "end": np.float64(23.921),
                    "score": np.float64(0.881),
                },
                {
                    "word": "genre",
                    "start": np.float64(23.941),
                    "end": np.float64(24.061),
                    "score": np.float64(0.276),
                },
                {
                    "word": "de",
                    "start": np.float64(24.081),
                    "end": np.float64(24.161),
                    "score": np.float64(0.527),
                },
                {
                    "word": "kamikaze.",
                    "start": np.float64(24.181),
                    "end": np.float64(24.802),
                    "score": np.float64(0.832),
                },
            ],
        },
        {
            "start": 24.862,
            "end": 26.444,
            "text": "Ok, ne bougez pas, je vais en parler à la DRH.",
            "words": [
                {
                    "word": "Ok,",
                    "start": np.float64(24.862),
                    "end": np.float64(25.002),
                    "score": np.float64(0.381),
                },
                {
                    "word": "ne",
                    "start": np.float64(25.042),
                    "end": np.float64(25.202),
                    "score": np.float64(0.406),
                },
                {
                    "word": "bougez",
                    "start": np.float64(25.222),
                    "end": np.float64(25.482),
                    "score": np.float64(0.783),
                },
                {
                    "word": "pas,",
                    "start": np.float64(25.502),
                    "end": np.float64(25.603),
                    "score": np.float64(0.797),
                },
                {
                    "word": "je",
                    "start": np.float64(25.643),
                    "end": np.float64(25.703),
                    "score": np.float64(0.842),
                },
                {
                    "word": "vais",
                    "start": np.float64(25.743),
                    "end": np.float64(25.823),
                    "score": np.float64(0.138),
                },
                {
                    "word": "en",
                    "start": np.float64(25.843),
                    "end": np.float64(25.883),
                    "score": np.float64(0.004),
                },
                {
                    "word": "parler",
                    "start": np.float64(25.903),
                    "end": np.float64(26.063),
                    "score": np.float64(0.797),
                },
                {
                    "word": "à",
                    "start": np.float64(26.083),
                    "end": np.float64(26.103),
                    "score": np.float64(0.055),
                },
                {
                    "word": "la",
                    "start": np.float64(26.123),
                    "end": np.float64(26.163),
                    "score": np.float64(0.004),
                },
                {
                    "word": "DRH.",
                    "start": np.float64(26.283),
                    "end": np.float64(26.444),
                    "score": np.float64(0.33),
                },
            ],
        },
        {
            "start": 31.537,
            "end": 32.898,
            "text": " Bienvenue Charles Caïda.",
            "words": [
                {
                    "word": "Bienvenue",
                    "start": np.float64(31.537),
                    "end": np.float64(32.057),
                    "score": np.float64(0.449),
                },
                {
                    "word": "Charles",
                    "start": np.float64(32.077),
                    "end": np.float64(32.318),
                    "score": np.float64(0.2),
                },
                {
                    "word": "Caïda.",
                    "start": np.float64(32.338),
                    "end": np.float64(32.898),
                    "score": np.float64(0.752),
                },
            ],
        },
        {
            "start": 32.938,
            "end": 35.8,
            "text": "Oui bonjour je voudrais réserver 5 billets à l'essence pour New York s'il vous plaît.",
            "words": [
                {
                    "word": "Oui",
                    "start": np.float64(32.938),
                    "end": np.float64(33.038),
                    "score": np.float64(0.225),
                },
                {
                    "word": "bonjour",
                    "start": np.float64(33.058),
                    "end": np.float64(33.258),
                    "score": np.float64(0.22),
                },
                {
                    "word": "je",
                    "start": np.float64(33.278),
                    "end": np.float64(33.318),
                    "score": np.float64(0.976),
                },
                {
                    "word": "voudrais",
                    "start": np.float64(33.338),
                    "end": np.float64(33.579),
                    "score": np.float64(0.766),
                },
                {
                    "word": "réserver",
                    "start": np.float64(33.619),
                    "end": np.float64(33.939),
                    "score": np.float64(0.822),
                },
                {"word": "5"},
                {
                    "word": "billets",
                    "start": np.float64(33.999),
                    "end": np.float64(34.359),
                    "score": np.float64(0.41),
                },
                {
                    "word": "à",
                    "start": np.float64(34.379),
                    "end": np.float64(34.399),
                    "score": np.float64(0.599),
                },
                {
                    "word": "l'essence",
                    "start": np.float64(34.439),
                    "end": np.float64(34.72),
                    "score": np.float64(0.578),
                },
                {
                    "word": "pour",
                    "start": np.float64(34.74),
                    "end": np.float64(34.86),
                    "score": np.float64(0.827),
                },
                {
                    "word": "New",
                    "start": np.float64(34.88),
                    "end": np.float64(34.96),
                    "score": np.float64(0.327),
                },
                {
                    "word": "York",
                    "start": np.float64(35.02),
                    "end": np.float64(35.22),
                    "score": np.float64(0.493),
                },
                {
                    "word": "s'il",
                    "start": np.float64(35.24),
                    "end": np.float64(35.32),
                    "score": np.float64(0.457),
                },
                {
                    "word": "vous",
                    "start": np.float64(35.34),
                    "end": np.float64(35.42),
                    "score": np.float64(0.611),
                },
                {
                    "word": "plaît.",
                    "start": np.float64(35.44),
                    "end": np.float64(35.8),
                    "score": np.float64(0.407),
                },
            ],
        },
        {
            "start": 35.86,
            "end": 36.341,
            "text": "En business.",
            "words": [
                {
                    "word": "En",
                    "start": np.float64(35.86),
                    "end": np.float64(35.901),
                    "score": np.float64(0.154),
                },
                {
                    "word": "business.",
                    "start": np.float64(35.921),
                    "end": np.float64(36.341),
                    "score": np.float64(0.403),
                },
            ],
        },
        {
            "start": 36.381,
            "end": 37.302,
            "text": "En business.",
            "words": [
                {
                    "word": "En",
                    "start": np.float64(36.381),
                    "end": np.float64(36.441),
                    "score": np.float64(0.428),
                },
                {
                    "word": "business.",
                    "start": np.float64(36.461),
                    "end": np.float64(37.302),
                    "score": np.float64(0.683),
                },
            ],
        },
        {
            "start": 37.342,
            "end": 40.664,
            "text": "Et oui alors question, est-ce que les armes et les bombes c'est considéré comme des bagages à main ?",
            "words": [
                {
                    "word": "Et",
                    "start": np.float64(37.342),
                    "end": np.float64(37.402),
                    "score": np.float64(0.344),
                },
                {
                    "word": "oui",
                    "start": np.float64(37.422),
                    "end": np.float64(37.562),
                    "score": np.float64(0.616),
                },
                {
                    "word": "alors",
                    "start": np.float64(37.602),
                    "end": np.float64(37.762),
                    "score": np.float64(0.606),
                },
                {
                    "word": "question,",
                    "start": np.float64(37.802),
                    "end": np.float64(38.302),
                    "score": np.float64(0.906),
                },
                {
                    "word": "est-ce",
                    "start": np.float64(38.342),
                    "end": np.float64(38.483),
                    "score": np.float64(0.692),
                },
                {
                    "word": "que",
                    "start": np.float64(38.503),
                    "end": np.float64(38.643),
                    "score": np.float64(0.719),
                },
                {
                    "word": "les",
                    "start": np.float64(38.663),
                    "end": np.float64(38.743),
                    "score": np.float64(0.964),
                },
                {
                    "word": "armes",
                    "start": np.float64(38.803),
                    "end": np.float64(38.963),
                    "score": np.float64(0.8),
                },
                {
                    "word": "et",
                    "start": np.float64(38.983),
                    "end": np.float64(39.023),
                    "score": np.float64(0.984),
                },
                {
                    "word": "les",
                    "start": np.float64(39.063),
                    "end": np.float64(39.163),
                    "score": np.float64(0.831),
                },
                {
                    "word": "bombes",
                    "start": np.float64(39.203),
                    "end": np.float64(39.403),
                    "score": np.float64(0.447),
                },
                {
                    "word": "c'est",
                    "start": np.float64(39.443),
                    "end": np.float64(39.563),
                    "score": np.float64(0.523),
                },
                {
                    "word": "considéré",
                    "start": np.float64(39.583),
                    "end": np.float64(39.904),
                    "score": np.float64(0.922),
                },
                {
                    "word": "comme",
                    "start": np.float64(39.924),
                    "end": np.float64(40.084),
                    "score": np.float64(0.886),
                },
                {
                    "word": "des",
                    "start": np.float64(40.104),
                    "end": np.float64(40.164),
                    "score": np.float64(0.813),
                },
                {
                    "word": "bagages",
                    "start": np.float64(40.184),
                    "end": np.float64(40.404),
                    "score": np.float64(0.804),
                },
                {
                    "word": "à",
                    "start": np.float64(40.444),
                    "end": np.float64(40.464),
                    "score": np.float64(0.203),
                },
                {
                    "word": "main",
                    "start": np.float64(40.484),
                    "end": np.float64(40.664),
                    "score": np.float64(0.443),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 40.704,
            "end": 41.665,
            "text": "On veut libérer nos frères !",
            "words": [
                {
                    "word": "On",
                    "start": np.float64(40.704),
                    "end": np.float64(40.784),
                    "score": np.float64(0.717),
                },
                {
                    "word": "veut",
                    "start": np.float64(40.804),
                    "end": np.float64(40.945),
                    "score": np.float64(0.77),
                },
                {
                    "word": "libérer",
                    "start": np.float64(40.965),
                    "end": np.float64(41.245),
                    "score": np.float64(0.848),
                },
                {
                    "word": "nos",
                    "start": np.float64(41.285),
                    "end": np.float64(41.385),
                    "score": np.float64(0.875),
                },
                {
                    "word": "frères",
                    "start": np.float64(41.405),
                    "end": np.float64(41.665),
                    "score": np.float64(0.712),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 41.945,
            "end": 42.666,
            "text": "Ouais !",
            "words": [
                {
                    "word": "Ouais",
                    "start": np.float64(41.945),
                    "end": np.float64(42.666),
                    "score": np.float64(0.635),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 42.746,
            "end": 44.628,
            "text": "Et on veut euh... Qu'est-ce qu'on veut ?",
            "words": [
                {
                    "word": "Et",
                    "start": np.float64(42.746),
                    "end": np.float64(42.846),
                    "score": np.float64(0.883),
                },
                {
                    "word": "on",
                    "start": np.float64(42.886),
                    "end": np.float64(42.946),
                    "score": np.float64(0.748),
                },
                {
                    "word": "veut",
                    "start": np.float64(42.986),
                    "end": np.float64(44.027),
                    "score": np.float64(0.735),
                },
                {
                    "word": "euh...",
                    "start": np.float64(44.067),
                    "end": np.float64(44.187),
                    "score": np.float64(0.34),
                },
                {
                    "word": "Qu'est-ce",
                    "start": np.float64(44.207),
                    "end": np.float64(44.367),
                    "score": np.float64(0.385),
                },
                {
                    "word": "qu'on",
                    "start": np.float64(44.387),
                    "end": np.float64(44.507),
                    "score": np.float64(0.796),
                },
                {
                    "word": "veut",
                    "start": np.float64(44.527),
                    "end": np.float64(44.628),
                    "score": np.float64(0.631),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 44.808,
            "end": 45.548,
            "text": "Des tickets restos.",
            "words": [
                {
                    "word": "Des",
                    "start": np.float64(44.808),
                    "end": np.float64(44.888),
                    "score": np.float64(0.45),
                },
                {
                    "word": "tickets",
                    "start": np.float64(44.908),
                    "end": np.float64(45.168),
                    "score": np.float64(0.396),
                },
                {
                    "word": "restos.",
                    "start": np.float64(45.188),
                    "end": np.float64(45.548),
                    "score": np.float64(0.895),
                },
            ],
        },
        {
            "start": 45.588,
            "end": 46.449,
            "text": "Ah on veut des tickets restos !",
            "words": [
                {
                    "word": "Ah",
                    "start": np.float64(45.588),
                    "end": np.float64(45.648),
                    "score": np.float64(0.268),
                },
                {
                    "word": "on",
                    "start": np.float64(45.688),
                    "end": np.float64(45.748),
                    "score": np.float64(0.926),
                },
                {
                    "word": "veut",
                    "start": np.float64(45.788),
                    "end": np.float64(45.889),
                    "score": np.float64(0.938),
                },
                {
                    "word": "des",
                    "start": np.float64(45.929),
                    "end": np.float64(45.989),
                    "score": np.float64(0.505),
                },
                {
                    "word": "tickets",
                    "start": np.float64(46.009),
                    "end": np.float64(46.269),
                    "score": np.float64(0.432),
                },
                {
                    "word": "restos",
                    "start": np.float64(46.289),
                    "end": np.float64(46.449),
                    "score": np.float64(0.646),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 46.489,
            "end": 47.33,
            "text": "Putain bande de con !",
            "words": [
                {
                    "word": "Putain",
                    "start": np.float64(46.489),
                    "end": np.float64(46.749),
                    "score": np.float64(0.351),
                },
                {
                    "word": "bande",
                    "start": np.float64(46.769),
                    "end": np.float64(46.929),
                    "score": np.float64(0.51),
                },
                {
                    "word": "de",
                    "start": np.float64(46.969),
                    "end": np.float64(47.07),
                    "score": np.float64(0.838),
                },
                {
                    "word": "con",
                    "start": np.float64(47.09),
                    "end": np.float64(47.33),
                    "score": np.float64(0.803),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 47.47,
            "end": 48.29,
            "text": "Des tickets restos !",
            "words": [
                {
                    "word": "Des",
                    "start": np.float64(47.47),
                    "end": np.float64(47.53),
                    "score": np.float64(0.404),
                },
                {
                    "word": "tickets",
                    "start": np.float64(47.55),
                    "end": np.float64(47.77),
                    "score": np.float64(0.421),
                },
                {
                    "word": "restos",
                    "start": np.float64(47.81),
                    "end": np.float64(48.29),
                    "score": np.float64(0.794),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 48.351,
            "end": 49.852,
            "text": "Imaginons je veux faire un attentat.",
            "words": [
                {
                    "word": "Imaginons",
                    "start": np.float64(48.351),
                    "end": np.float64(48.831),
                    "score": np.float64(0.897),
                },
                {
                    "word": "je",
                    "start": np.float64(48.871),
                    "end": np.float64(48.931),
                    "score": np.float64(0.748),
                },
                {
                    "word": "veux",
                    "start": np.float64(48.951),
                    "end": np.float64(49.071),
                    "score": np.float64(0.806),
                },
                {
                    "word": "faire",
                    "start": np.float64(49.111),
                    "end": np.float64(49.251),
                    "score": np.float64(0.698),
                },
                {
                    "word": "un",
                    "start": np.float64(49.271),
                    "end": np.float64(49.331),
                    "score": np.float64(0.602),
                },
                {
                    "word": "attentat.",
                    "start": np.float64(49.371),
                    "end": np.float64(49.852),
                    "score": np.float64(0.976),
                },
            ],
        },
        {
            "start": 49.892,
            "end": 50.592,
            "text": "Hypothèse.",
            "words": [
                {
                    "word": "Hypothèse.",
                    "start": np.float64(49.892),
                    "end": np.float64(50.592),
                    "score": np.float64(0.858),
                }
            ],
        },
        {
            "start": 50.652,
            "end": 51.153,
            "text": "Hypothèse.",
            "words": [
                {
                    "word": "Hypothèse.",
                    "start": np.float64(50.652),
                    "end": np.float64(51.153),
                    "score": np.float64(0.943),
                }
            ],
        },
        {
            "start": 51.193,
            "end": 54.736,
            "text": "Ce serait quoi la meilleure fourchette horaire pour faire un carnage ?",
            "words": [
                {
                    "word": "Ce",
                    "start": np.float64(51.193),
                    "end": np.float64(51.273),
                    "score": np.float64(0.917),
                },
                {
                    "word": "serait",
                    "start": np.float64(51.293),
                    "end": np.float64(51.513),
                    "score": np.float64(0.84),
                },
                {
                    "word": "quoi",
                    "start": np.float64(51.553),
                    "end": np.float64(51.773),
                    "score": np.float64(0.853),
                },
                {
                    "word": "la",
                    "start": np.float64(51.833),
                    "end": np.float64(51.993),
                    "score": np.float64(0.937),
                },
                {
                    "word": "meilleure",
                    "start": np.float64(52.034),
                    "end": np.float64(52.434),
                    "score": np.float64(0.773),
                },
                {
                    "word": "fourchette",
                    "start": np.float64(52.494),
                    "end": np.float64(52.894),
                    "score": np.float64(0.829),
                },
                {
                    "word": "horaire",
                    "start": np.float64(52.934),
                    "end": np.float64(53.535),
                    "score": np.float64(0.755),
                },
                {
                    "word": "pour",
                    "start": np.float64(53.555),
                    "end": np.float64(53.695),
                    "score": np.float64(0.834),
                },
                {
                    "word": "faire",
                    "start": np.float64(53.735),
                    "end": np.float64(53.895),
                    "score": np.float64(0.886),
                },
                {
                    "word": "un",
                    "start": np.float64(53.955),
                    "end": np.float64(53.995),
                    "score": np.float64(0.538),
                },
                {
                    "word": "carnage",
                    "start": np.float64(54.015),
                    "end": np.float64(54.736),
                    "score": np.float64(0.962),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 54.796,
            "end": 55.676,
            "text": "Grosso merdo hein.",
            "words": [
                {
                    "word": "Grosso",
                    "start": np.float64(54.796),
                    "end": np.float64(55.056),
                    "score": np.float64(0.402),
                },
                {
                    "word": "merdo",
                    "start": np.float64(55.076),
                    "end": np.float64(55.376),
                    "score": np.float64(0.768),
                },
                {
                    "word": "hein.",
                    "start": np.float64(55.416),
                    "end": np.float64(55.676),
                    "score": np.float64(0.334),
                },
            ],
        },
        {
            "start": 55.736,
            "end": 55.977,
            "text": "Oh euh 10h30.",
            "words": [
                {
                    "word": "Oh",
                    "start": np.float64(55.736),
                    "end": np.float64(55.797),
                    "score": np.float64(0.235),
                },
                {
                    "word": "euh",
                    "start": np.float64(55.857),
                    "end": np.float64(55.917),
                    "score": np.float64(0.041),
                },
                {
                    "word": "10h30.",
                    "start": np.float64(55.957),
                    "end": np.float64(55.977),
                    "score": np.float64(0.003),
                },
            ],
        },
        {
            "start": 56.818,
            "end": 59.019,
            "text": " Nous ne ferons pas de quartier et nous n'aurons aucune pitié.",
            "words": [
                {
                    "word": "Nous",
                    "start": np.float64(56.818),
                    "end": np.float64(56.918),
                    "score": np.float64(0.871),
                },
                {
                    "word": "ne",
                    "start": np.float64(56.938),
                    "end": np.float64(56.998),
                    "score": np.float64(0.759),
                },
                {
                    "word": "ferons",
                    "start": np.float64(57.018),
                    "end": np.float64(57.218),
                    "score": np.float64(0.75),
                },
                {
                    "word": "pas",
                    "start": np.float64(57.238),
                    "end": np.float64(57.298),
                    "score": np.float64(0.999),
                },
                {
                    "word": "de",
                    "start": np.float64(57.318),
                    "end": np.float64(57.378),
                    "score": np.float64(0.762),
                },
                {
                    "word": "quartier",
                    "start": np.float64(57.398),
                    "end": np.float64(57.939),
                    "score": np.float64(0.92),
                },
                {
                    "word": "et",
                    "start": np.float64(57.999),
                    "end": np.float64(58.039),
                    "score": np.float64(0.903),
                },
                {
                    "word": "nous",
                    "start": np.float64(58.059),
                    "end": np.float64(58.159),
                    "score": np.float64(0.886),
                },
                {
                    "word": "n'aurons",
                    "start": np.float64(58.179),
                    "end": np.float64(58.459),
                    "score": np.float64(0.708),
                },
                {
                    "word": "aucune",
                    "start": np.float64(58.499),
                    "end": np.float64(58.719),
                    "score": np.float64(0.833),
                },
                {
                    "word": "pitié.",
                    "start": np.float64(58.759),
                    "end": np.float64(59.019),
                    "score": np.float64(0.769),
                },
            ],
        },
        {
            "start": 59.719,
            "end": 60.54,
            "text": "Ah mais qu'est-ce tu fais ?",
            "words": [
                {
                    "word": "Ah",
                    "start": np.float64(59.719),
                    "end": np.float64(59.779),
                    "score": np.float64(0.252),
                },
                {
                    "word": "mais",
                    "start": np.float64(59.799),
                    "end": np.float64(59.879),
                    "score": np.float64(0.242),
                },
                {
                    "word": "qu'est-ce",
                    "start": np.float64(59.899),
                    "end": np.float64(60.06),
                    "score": np.float64(0.199),
                },
                {
                    "word": "tu",
                    "start": np.float64(60.08),
                    "end": np.float64(60.14),
                    "score": np.float64(0.131),
                },
                {
                    "word": "fais",
                    "start": np.float64(60.16),
                    "end": np.float64(60.54),
                    "score": np.float64(0.817),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 60.58,
            "end": 61.32,
            "text": "Mais je te fais un raccord mec.",
            "words": [
                {
                    "word": "Mais",
                    "start": np.float64(60.58),
                    "end": np.float64(60.66),
                    "score": np.float64(0.252),
                },
                {
                    "word": "je",
                    "start": np.float64(60.68),
                    "end": np.float64(60.74),
                    "score": np.float64(0.332),
                },
                {
                    "word": "te",
                    "start": np.float64(60.76),
                    "end": np.float64(60.82),
                    "score": np.float64(0.25),
                },
                {
                    "word": "fais",
                    "start": np.float64(60.84),
                    "end": np.float64(60.92),
                    "score": np.float64(0.176),
                },
                {
                    "word": "un",
                    "start": np.float64(60.96),
                    "end": np.float64(61.0),
                    "score": np.float64(0.035),
                },
                {
                    "word": "raccord",
                    "start": np.float64(61.02),
                    "end": np.float64(61.2),
                    "score": np.float64(0.338),
                },
                {
                    "word": "mec.",
                    "start": np.float64(61.22),
                    "end": np.float64(61.32),
                    "score": np.float64(0.383),
                },
            ],
        },
        {
            "start": 61.34,
            "end": 62.601,
            "text": "Mais j'enregistre un message, qu'est-ce toi ?",
            "words": [
                {
                    "word": "Mais",
                    "start": np.float64(61.34),
                    "end": np.float64(61.42),
                    "score": np.float64(0.553),
                },
                {
                    "word": "j'enregistre",
                    "start": np.float64(61.44),
                    "end": np.float64(61.8),
                    "score": np.float64(0.805),
                },
                {
                    "word": "un",
                    "start": np.float64(61.86),
                    "end": np.float64(61.92),
                    "score": np.float64(0.635),
                },
                {
                    "word": "message,",
                    "start": np.float64(61.94),
                    "end": np.float64(62.261),
                    "score": np.float64(0.786),
                },
                {
                    "word": "qu'est-ce",
                    "start": np.float64(62.281),
                    "end": np.float64(62.441),
                    "score": np.float64(0.155),
                },
                {
                    "word": "toi",
                    "start": np.float64(62.461),
                    "end": np.float64(62.601),
                    "score": np.float64(0.486),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 63.201,
            "end": 64.041,
            "text": "Psst !",
            "words": [
                {
                    "word": "Psst",
                    "start": np.float64(63.201),
                    "end": np.float64(64.041),
                    "score": np.float64(0.388),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 64.101,
            "end": 65.162,
            "text": "Quoi ?",
            "words": [
                {
                    "word": "Quoi",
                    "start": np.float64(64.101),
                    "end": np.float64(65.162),
                    "score": np.float64(0.691),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 65.222,
            "end": 66.783,
            "text": "Tu brilles, ça me gêne.",
            "words": [
                {
                    "word": "Tu",
                    "start": np.float64(65.222),
                    "end": np.float64(65.362),
                    "score": np.float64(0.612),
                },
                {
                    "word": "brilles,",
                    "start": np.float64(65.402),
                    "end": np.float64(66.002),
                    "score": np.float64(0.508),
                },
                {
                    "word": "ça",
                    "start": np.float64(66.022),
                    "end": np.float64(66.122),
                    "score": np.float64(0.636),
                },
                {
                    "word": "me",
                    "start": np.float64(66.142),
                    "end": np.float64(66.202),
                    "score": np.float64(0.65),
                },
                {
                    "word": "gêne.",
                    "start": np.float64(66.222),
                    "end": np.float64(66.783),
                    "score": np.float64(0.863),
                },
            ],
        },
        {
            "start": 66.803,
            "end": 68.303,
            "text": "Bon, on a encore une idée avec l'otage.",
            "words": [
                {
                    "word": "Bon,",
                    "start": np.float64(66.803),
                    "end": np.float64(66.963),
                    "score": np.float64(0.437),
                },
                {
                    "word": "on",
                    "start": np.float64(67.023),
                    "end": np.float64(67.083),
                    "score": np.float64(0.771),
                },
                {
                    "word": "a",
                    "start": np.float64(67.123),
                    "end": np.float64(67.203),
                    "score": np.float64(0.802),
                },
                {
                    "word": "encore",
                    "start": np.float64(67.223),
                    "end": np.float64(67.423),
                    "score": np.float64(0.818),
                },
                {
                    "word": "une",
                    "start": np.float64(67.463),
                    "end": np.float64(67.543),
                    "score": np.float64(0.751),
                },
                {
                    "word": "idée",
                    "start": np.float64(67.583),
                    "end": np.float64(67.703),
                    "score": np.float64(0.609),
                },
                {
                    "word": "avec",
                    "start": np.float64(67.723),
                    "end": np.float64(67.843),
                    "score": np.float64(0.24),
                },
                {
                    "word": "l'otage.",
                    "start": np.float64(67.883),
                    "end": np.float64(68.303),
                    "score": np.float64(0.541),
                },
            ],
        },
        {
            "start": 68.343,
            "end": 69.644,
            "text": "Quoi ?",
            "words": [
                {
                    "word": "Quoi",
                    "start": np.float64(68.343),
                    "end": np.float64(69.644),
                    "score": np.float64(0.639),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 69.684,
            "end": 71.265,
            "text": "C'est pas une bonne idée d'y aller en avion.",
            "words": [
                {
                    "word": "C'est",
                    "start": np.float64(69.684),
                    "end": np.float64(69.944),
                    "score": np.float64(0.629),
                },
                {
                    "word": "pas",
                    "start": np.float64(69.984),
                    "end": np.float64(70.104),
                    "score": np.float64(0.893),
                },
                {
                    "word": "une",
                    "start": np.float64(70.144),
                    "end": np.float64(70.244),
                    "score": np.float64(0.759),
                },
                {
                    "word": "bonne",
                    "start": np.float64(70.264),
                    "end": np.float64(70.444),
                    "score": np.float64(0.666),
                },
                {
                    "word": "idée",
                    "start": np.float64(70.464),
                    "end": np.float64(70.684),
                    "score": np.float64(0.664),
                },
                {
                    "word": "d'y",
                    "start": np.float64(70.704),
                    "end": np.float64(70.805),
                    "score": np.float64(0.548),
                },
                {
                    "word": "aller",
                    "start": np.float64(70.825),
                    "end": np.float64(71.025),
                    "score": np.float64(0.326),
                },
                {
                    "word": "en",
                    "start": np.float64(71.065),
                    "end": np.float64(71.125),
                    "score": np.float64(0.245),
                },
                {
                    "word": "avion.",
                    "start": np.float64(71.145),
                    "end": np.float64(71.265),
                    "score": np.float64(0.173),
                },
            ],
        },
        {
            "start": 71.645,
            "end": 73.446,
            "text": "On va se faire mal, c'est dangereux.",
            "words": [
                {
                    "word": "On",
                    "start": np.float64(71.645),
                    "end": np.float64(71.785),
                    "score": np.float64(0.634),
                },
                {
                    "word": "va",
                    "start": np.float64(71.805),
                    "end": np.float64(71.925),
                    "score": np.float64(0.518),
                },
                {
                    "word": "se",
                    "start": np.float64(71.945),
                    "end": np.float64(72.045),
                    "score": np.float64(0.701),
                },
                {
                    "word": "faire",
                    "start": np.float64(72.065),
                    "end": np.float64(72.245),
                    "score": np.float64(0.408),
                },
                {
                    "word": "mal,",
                    "start": np.float64(72.265),
                    "end": np.float64(72.705),
                    "score": np.float64(0.885),
                },
                {
                    "word": "c'est",
                    "start": np.float64(72.725),
                    "end": np.float64(72.865),
                    "score": np.float64(0.852),
                },
                {
                    "word": "dangereux.",
                    "start": np.float64(72.905),
                    "end": np.float64(73.446),
                    "score": np.float64(0.706),
                },
            ],
        },
        {
            "start": 73.466,
            "end": 75.106,
            "text": "Moi je dis, faut y aller en vélo.",
            "words": [
                {
                    "word": "Moi",
                    "start": np.float64(73.466),
                    "end": np.float64(73.566),
                    "score": np.float64(0.507),
                },
                {
                    "word": "je",
                    "start": np.float64(73.586),
                    "end": np.float64(73.666),
                    "score": np.float64(0.686),
                },
                {
                    "word": "dis,",
                    "start": np.float64(73.686),
                    "end": np.float64(73.766),
                    "score": np.float64(0.574),
                },
                {
                    "word": "faut",
                    "start": np.float64(73.786),
                    "end": np.float64(73.886),
                    "score": np.float64(0.302),
                },
                {
                    "word": "y",
                    "start": np.float64(73.926),
                    "end": np.float64(73.966),
                    "score": np.float64(0.237),
                },
                {
                    "word": "aller",
                    "start": np.float64(73.986),
                    "end": np.float64(74.086),
                    "score": np.float64(0.107),
                },
                {
                    "word": "en",
                    "start": np.float64(74.106),
                    "end": np.float64(74.186),
                    "score": np.float64(0.46),
                },
                {
                    "word": "vélo.",
                    "start": np.float64(74.206),
                    "end": np.float64(75.106),
                    "score": np.float64(0.606),
                },
            ],
        },
        {
            "start": 75.127,
            "end": 75.687,
            "text": "Voilà.",
            "words": [
                {
                    "word": "Voilà.",
                    "start": np.float64(75.127),
                    "end": np.float64(75.687),
                    "score": np.float64(0.483),
                }
            ],
        },
        {
            "start": 75.707,
            "end": 76.647,
            "text": "Pourquoi ?",
            "words": [
                {
                    "word": "Pourquoi",
                    "start": np.float64(75.707),
                    "end": np.float64(76.647),
                    "score": np.float64(0.87),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 76.807,
            "end": 77.688,
            "text": "Développement durable.",
            "words": [
                {
                    "word": "Développement",
                    "start": np.float64(76.807),
                    "end": np.float64(77.348),
                    "score": np.float64(0.931),
                },
                {
                    "word": "durable.",
                    "start": np.float64(77.388),
                    "end": np.float64(77.688),
                    "score": np.float64(0.84),
                },
            ],
        },
        {
            "start": 77.728,
            "end": 80.009,
            "text": "Car vous ne briserez jamais notre solidarité.",
            "words": [
                {
                    "word": "Car",
                    "start": np.float64(77.728),
                    "end": np.float64(77.828),
                    "score": np.float64(0.95),
                },
                {
                    "word": "vous",
                    "start": np.float64(77.868),
                    "end": np.float64(77.968),
                    "score": np.float64(0.886),
                },
                {
                    "word": "ne",
                    "start": np.float64(77.988),
                    "end": np.float64(78.048),
                    "score": np.float64(0.772),
                },
                {
                    "word": "briserez",
                    "start": np.float64(78.088),
                    "end": np.float64(78.408),
                    "score": np.float64(0.92),
                },
                {
                    "word": "jamais",
                    "start": np.float64(78.448),
                    "end": np.float64(78.648),
                    "score": np.float64(0.894),
                },
                {
                    "word": "notre",
                    "start": np.float64(78.708),
                    "end": np.float64(78.848),
                    "score": np.float64(0.903),
                },
                {
                    "word": "solidarité.",
                    "start": np.float64(78.888),
                    "end": np.float64(80.009),
                    "score": np.float64(0.926),
                },
            ],
        },
        {
            "start": 80.029,
            "end": 80.589,
            "text": "Quoi ?",
            "words": [
                {
                    "word": "Quoi",
                    "start": np.float64(80.029),
                    "end": np.float64(80.589),
                    "score": np.float64(0.644),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 80.629,
            "end": 81.97,
            "text": "Remets ton chèche.",
            "words": [
                {
                    "word": "Remets",
                    "start": np.float64(80.629),
                    "end": np.float64(80.849),
                    "score": np.float64(0.331),
                },
                {
                    "word": "ton",
                    "start": np.float64(80.869),
                    "end": np.float64(81.029),
                    "score": np.float64(0.525),
                },
                {
                    "word": "chèche.",
                    "start": np.float64(81.049),
                    "end": np.float64(81.97),
                    "score": np.float64(0.795),
                },
            ],
        },
        {
            "start": 82.53,
            "end": 83.63,
            "text": "On a les cinq cordelettes ?",
            "words": [
                {
                    "word": "On",
                    "start": np.float64(82.53),
                    "end": np.float64(82.61),
                    "score": np.float64(0.601),
                },
                {
                    "word": "a",
                    "start": np.float64(82.67),
                    "end": np.float64(82.73),
                    "score": np.float64(0.613),
                },
                {
                    "word": "les",
                    "start": np.float64(82.75),
                    "end": np.float64(82.99),
                    "score": np.float64(0.765),
                },
                {
                    "word": "cinq",
                    "start": np.float64(83.01),
                    "end": np.float64(83.21),
                    "score": np.float64(0.438),
                },
                {
                    "word": "cordelettes",
                    "start": np.float64(83.25),
                    "end": np.float64(83.63),
                    "score": np.float64(0.442),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 83.71,
            "end": 84.371,
            "text": "Non, on n'a que trois.",
            "words": [
                {
                    "word": "Non,",
                    "start": np.float64(83.71),
                    "end": np.float64(83.871),
                    "score": np.float64(0.571),
                },
                {
                    "word": "on",
                    "start": np.float64(83.951),
                    "end": np.float64(84.051),
                    "score": np.float64(0.361),
                },
                {
                    "word": "n'a",
                    "start": np.float64(84.091),
                    "end": np.float64(84.131),
                    "score": np.float64(0.009),
                },
                {
                    "word": "que",
                    "start": np.float64(84.151),
                    "end": np.float64(84.251),
                    "score": np.float64(0.199),
                },
                {
                    "word": "trois.",
                    "start": np.float64(84.271),
                    "end": np.float64(84.371),
                    "score": np.float64(0.223),
                },
            ],
        },
        {
            "start": 85.121,
            "end": 85.681,
            "text": " Il n'y en a que trois ?",
            "words": [
                {
                    "word": "Il",
                    "start": np.float64(85.121),
                    "end": np.float64(85.161),
                    "score": np.float64(0.006),
                },
                {
                    "word": "n'y",
                    "start": np.float64(85.181),
                    "end": np.float64(85.221),
                    "score": np.float64(0.015),
                },
                {
                    "word": "en",
                    "start": np.float64(85.281),
                    "end": np.float64(85.321),
                    "score": np.float64(0.044),
                },
                {
                    "word": "a",
                    "start": np.float64(85.341),
                    "end": np.float64(85.361),
                    "score": np.float64(0.004),
                },
                {
                    "word": "que",
                    "start": np.float64(85.381),
                    "end": np.float64(85.521),
                    "score": np.float64(0.334),
                },
                {
                    "word": "trois",
                    "start": np.float64(85.541),
                    "end": np.float64(85.681),
                    "score": np.float64(0.645),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 86.062,
            "end": 86.562,
            "text": "Bah ouais.",
            "words": [
                {
                    "word": "Bah",
                    "start": np.float64(86.062),
                    "end": np.float64(86.222),
                    "score": np.float64(0.255),
                },
                {
                    "word": "ouais.",
                    "start": np.float64(86.262),
                    "end": np.float64(86.562),
                    "score": np.float64(0.45),
                },
            ],
        },
        {
            "start": 86.602,
            "end": 88.884,
            "text": "Putain ils ont un médecin et qu'ils font chier ces suédois là.",
            "words": [
                {
                    "word": "Putain",
                    "start": np.float64(86.602),
                    "end": np.float64(86.802),
                    "score": np.float64(0.29),
                },
                {
                    "word": "ils",
                    "start": np.float64(86.842),
                    "end": np.float64(86.902),
                    "score": np.float64(0.29),
                },
                {
                    "word": "ont",
                    "start": np.float64(86.942),
                    "end": np.float64(87.003),
                    "score": np.float64(0.444),
                },
                {
                    "word": "un",
                    "start": np.float64(87.063),
                    "end": np.float64(87.103),
                    "score": np.float64(0.017),
                },
                {
                    "word": "médecin",
                    "start": np.float64(87.123),
                    "end": np.float64(87.363),
                    "score": np.float64(0.258),
                },
                {
                    "word": "et",
                    "start": np.float64(87.383),
                    "end": np.float64(87.423),
                    "score": np.float64(0.007),
                },
                {
                    "word": "qu'ils",
                    "start": np.float64(87.443),
                    "end": np.float64(87.563),
                    "score": np.float64(0.166),
                },
                {
                    "word": "font",
                    "start": np.float64(87.583),
                    "end": np.float64(87.783),
                    "score": np.float64(0.733),
                },
                {
                    "word": "chier",
                    "start": np.float64(87.843),
                    "end": np.float64(88.163),
                    "score": np.float64(0.799),
                },
                {
                    "word": "ces",
                    "start": np.float64(88.203),
                    "end": np.float64(88.344),
                    "score": np.float64(0.827),
                },
                {
                    "word": "suédois",
                    "start": np.float64(88.384),
                    "end": np.float64(88.784),
                    "score": np.float64(0.808),
                },
                {
                    "word": "là.",
                    "start": np.float64(88.804),
                    "end": np.float64(88.884),
                    "score": np.float64(0.32),
                },
            ],
        },
        {
            "start": 88.904,
            "end": 90.585,
            "text": "C'est les prochains qu'on fait péter moi je vous le dis.",
            "words": [
                {
                    "word": "C'est",
                    "start": np.float64(88.904),
                    "end": np.float64(89.024),
                    "score": np.float64(0.587),
                },
                {
                    "word": "les",
                    "start": np.float64(89.044),
                    "end": np.float64(89.124),
                    "score": np.float64(0.721),
                },
                {
                    "word": "prochains",
                    "start": np.float64(89.164),
                    "end": np.float64(89.384),
                    "score": np.float64(0.93),
                },
                {
                    "word": "qu'on",
                    "start": np.float64(89.424),
                    "end": np.float64(89.565),
                    "score": np.float64(0.824),
                },
                {
                    "word": "fait",
                    "start": np.float64(89.585),
                    "end": np.float64(89.685),
                    "score": np.float64(0.776),
                },
                {
                    "word": "péter",
                    "start": np.float64(89.725),
                    "end": np.float64(89.905),
                    "score": np.float64(0.567),
                },
                {
                    "word": "moi",
                    "start": np.float64(89.945),
                    "end": np.float64(90.025),
                    "score": np.float64(0.669),
                },
                {
                    "word": "je",
                    "start": np.float64(90.045),
                    "end": np.float64(90.085),
                    "score": np.float64(0.794),
                },
                {
                    "word": "vous",
                    "start": np.float64(90.105),
                    "end": np.float64(90.205),
                    "score": np.float64(0.832),
                },
                {
                    "word": "le",
                    "start": np.float64(90.245),
                    "end": np.float64(90.285),
                    "score": np.float64(0.97),
                },
                {
                    "word": "dis.",
                    "start": np.float64(90.305),
                    "end": np.float64(90.585),
                    "score": np.float64(0.857),
                },
            ],
        },
        {
            "start": 90.605,
            "end": 94.288,
            "text": "Je vends ce superbe dragonneuf qui n'a servi que très peu de fois.",
            "words": [
                {
                    "word": "Je",
                    "start": np.float64(90.605),
                    "end": np.float64(90.665),
                    "score": np.float64(0.77),
                },
                {
                    "word": "vends",
                    "start": np.float64(90.705),
                    "end": np.float64(90.906),
                    "score": np.float64(0.651),
                },
                {
                    "word": "ce",
                    "start": np.float64(90.946),
                    "end": np.float64(91.086),
                    "score": np.float64(0.887),
                },
                {
                    "word": "superbe",
                    "start": np.float64(91.126),
                    "end": np.float64(91.546),
                    "score": np.float64(0.951),
                },
                {
                    "word": "dragonneuf",
                    "start": np.float64(91.566),
                    "end": np.float64(92.026),
                    "score": np.float64(0.829),
                },
                {
                    "word": "qui",
                    "start": np.float64(92.067),
                    "end": np.float64(92.187),
                    "score": np.float64(0.897),
                },
                {
                    "word": "n'a",
                    "start": np.float64(92.207),
                    "end": np.float64(92.287),
                    "score": np.float64(0.914),
                },
                {
                    "word": "servi",
                    "start": np.float64(92.327),
                    "end": np.float64(92.647),
                    "score": np.float64(0.913),
                },
                {
                    "word": "que",
                    "start": np.float64(92.687),
                    "end": np.float64(92.807),
                    "score": np.float64(0.937),
                },
                {
                    "word": "très",
                    "start": np.float64(92.847),
                    "end": np.float64(92.987),
                    "score": np.float64(0.784),
                },
                {
                    "word": "peu",
                    "start": np.float64(93.007),
                    "end": np.float64(93.127),
                    "score": np.float64(0.851),
                },
                {
                    "word": "de",
                    "start": np.float64(93.167),
                    "end": np.float64(93.247),
                    "score": np.float64(0.958),
                },
                {
                    "word": "fois.",
                    "start": np.float64(93.287),
                    "end": np.float64(94.288),
                    "score": np.float64(0.915),
                },
            ],
        },
        {
            "start": 94.328,
            "end": 95.209,
            "text": "Facilement maniable.",
            "words": [
                {
                    "word": "Facilement",
                    "start": np.float64(94.328),
                    "end": np.float64(94.709),
                    "score": np.float64(0.956),
                },
                {
                    "word": "maniable.",
                    "start": np.float64(94.769),
                    "end": np.float64(95.209),
                    "score": np.float64(0.909),
                },
            ],
        },
        {
            "start": 95.589,
            "end": 98.011,
            "text": "On peut savoir ce que tu fous là ?",
            "words": [
                {
                    "word": "On",
                    "start": np.float64(95.589),
                    "end": np.float64(95.669),
                    "score": np.float64(0.498),
                },
                {
                    "word": "peut",
                    "start": np.float64(95.87),
                    "end": np.float64(97.251),
                    "score": np.float64(0.248),
                },
                {
                    "word": "savoir",
                    "start": np.float64(97.271),
                    "end": np.float64(97.391),
                    "score": np.float64(0.135),
                },
                {
                    "word": "ce",
                    "start": np.float64(97.411),
                    "end": np.float64(97.471),
                    "score": np.float64(0.806),
                },
                {
                    "word": "que",
                    "start": np.float64(97.491),
                    "end": np.float64(97.571),
                    "score": np.float64(0.872),
                },
                {
                    "word": "tu",
                    "start": np.float64(97.591),
                    "end": np.float64(97.731),
                    "score": np.float64(0.633),
                },
                {
                    "word": "fous",
                    "start": np.float64(97.751),
                    "end": np.float64(97.851),
                    "score": np.float64(0.332),
                },
                {
                    "word": "là",
                    "start": np.float64(97.871),
                    "end": np.float64(98.011),
                    "score": np.float64(0.614),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 98.251,
            "end": 99.893,
            "text": "On ne cédera pas au capitalisme américain !",
            "words": [
                {
                    "word": "On",
                    "start": np.float64(98.251),
                    "end": np.float64(98.331),
                    "score": np.float64(0.431),
                },
                {
                    "word": "ne",
                    "start": np.float64(98.351),
                    "end": np.float64(98.452),
                    "score": np.float64(0.356),
                },
                {
                    "word": "cédera",
                    "start": np.float64(98.472),
                    "end": np.float64(98.732),
                    "score": np.float64(0.845),
                },
                {
                    "word": "pas",
                    "start": np.float64(98.772),
                    "end": np.float64(98.872),
                    "score": np.float64(0.654),
                },
                {
                    "word": "au",
                    "start": np.float64(98.912),
                    "end": np.float64(98.972),
                    "score": np.float64(0.967),
                },
                {
                    "word": "capitalisme",
                    "start": np.float64(99.012),
                    "end": np.float64(99.472),
                    "score": np.float64(0.913),
                },
                {
                    "word": "américain",
                    "start": np.float64(99.512),
                    "end": np.float64(99.893),
                    "score": np.float64(0.893),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 100.113,
            "end": 100.453,
            "text": "Ouais !",
            "words": [
                {
                    "word": "Ouais",
                    "start": np.float64(100.113),
                    "end": np.float64(100.453),
                    "score": np.float64(0.525),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 101.654,
            "end": 102.395,
            "text": "Et voilà vos burgers !",
            "words": [
                {
                    "word": "Et",
                    "start": np.float64(101.654),
                    "end": np.float64(101.714),
                    "score": np.float64(0.283),
                },
                {
                    "word": "voilà",
                    "start": np.float64(101.734),
                    "end": np.float64(101.894),
                    "score": np.float64(0.626),
                },
                {
                    "word": "vos",
                    "start": np.float64(101.914),
                    "end": np.float64(102.014),
                    "score": np.float64(0.24),
                },
                {
                    "word": "burgers",
                    "start": np.float64(102.034),
                    "end": np.float64(102.395),
                    "score": np.float64(0.687),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 102.435,
            "end": 102.715,
            "text": "Ouais !",
            "words": [
                {
                    "word": "Ouais",
                    "start": np.float64(102.435),
                    "end": np.float64(102.715),
                    "score": np.float64(0.193),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 102.775,
            "end": 103.175,
            "text": "Ah cool !",
            "words": [
                {
                    "word": "Ah",
                    "start": np.float64(102.775),
                    "end": np.float64(102.955),
                    "score": np.float64(0.722),
                },
                {
                    "word": "cool",
                    "start": np.float64(102.975),
                    "end": np.float64(103.175),
                    "score": np.float64(0.5),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 103.255,
            "end": 103.796,
            "text": "Qu'est-ce qu'il y a ?",
            "words": [
                {
                    "word": "Qu'est-ce",
                    "start": np.float64(103.255),
                    "end": np.float64(103.596),
                    "score": np.float64(0.534),
                },
                {
                    "word": "qu'il",
                    "start": np.float64(103.616),
                    "end": np.float64(103.716),
                    "score": np.float64(0.624),
                },
                {
                    "word": "y",
                    "start": np.float64(103.736),
                    "end": np.float64(103.756),
                    "score": np.float64(0.219),
                },
                {
                    "word": "a",
                    "start": np.float64(103.776),
                    "end": np.float64(103.796),
                    "score": np.float64(0.102),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 103.856,
            "end": 106.198,
            "text": "Il y a l'otache qui a encore une idée vachement bien.",
            "words": [
                {
                    "word": "Il",
                    "start": np.float64(103.856),
                    "end": np.float64(103.936),
                    "score": np.float64(0.3),
                },
                {
                    "word": "y",
                    "start": np.float64(104.096),
                    "end": np.float64(104.156),
                    "score": np.float64(0.631),
                },
                {
                    "word": "a",
                    "start": np.float64(104.236),
                    "end": np.float64(104.336),
                    "score": np.float64(0.711),
                },
                {
                    "word": "l'otache",
                    "start": np.float64(104.356),
                    "end": np.float64(104.736),
                    "score": np.float64(0.647),
                },
                {
                    "word": "qui",
                    "start": np.float64(104.757),
                    "end": np.float64(104.837),
                    "score": np.float64(0.827),
                },
                {
                    "word": "a",
                    "start": np.float64(104.877),
                    "end": np.float64(104.937),
                    "score": np.float64(0.347),
                },
                {
                    "word": "encore",
                    "start": np.float64(104.977),
                    "end": np.float64(105.157),
                    "score": np.float64(0.871),
                },
                {
                    "word": "une",
                    "start": np.float64(105.197),
                    "end": np.float64(105.297),
                    "score": np.float64(0.377),
                },
                {
                    "word": "idée",
                    "start": np.float64(105.337),
                    "end": np.float64(105.597),
                    "score": np.float64(0.638),
                },
                {
                    "word": "vachement",
                    "start": np.float64(105.637),
                    "end": np.float64(105.977),
                    "score": np.float64(0.448),
                },
                {
                    "word": "bien.",
                    "start": np.float64(105.997),
                    "end": np.float64(106.198),
                    "score": np.float64(0.452),
                },
            ],
        },
        {
            "start": 106.218,
            "end": 107.739,
            "text": "Je tourne une vidéo là !",
            "words": [
                {
                    "word": "Je",
                    "start": np.float64(106.218),
                    "end": np.float64(106.298),
                    "score": np.float64(0.394),
                },
                {
                    "word": "tourne",
                    "start": np.float64(106.318),
                    "end": np.float64(106.538),
                    "score": np.float64(0.426),
                },
                {
                    "word": "une",
                    "start": np.float64(106.598),
                    "end": np.float64(106.658),
                    "score": np.float64(0.034),
                },
                {
                    "word": "vidéo",
                    "start": np.float64(106.678),
                    "end": np.float64(107.118),
                    "score": np.float64(0.69),
                },
                {
                    "word": "là",
                    "start": np.float64(107.138),
                    "end": np.float64(107.739),
                    "score": np.float64(0.745),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 107.779,
            "end": 109.56,
            "text": "Non mais écoute, écoute.",
            "words": [
                {
                    "word": "Non",
                    "start": np.float64(107.779),
                    "end": np.float64(107.859),
                    "score": np.float64(0.212),
                },
                {
                    "word": "mais",
                    "start": np.float64(107.879),
                    "end": np.float64(107.979),
                    "score": np.float64(0.216),
                },
                {
                    "word": "écoute,",
                    "start": np.float64(108.039),
                    "end": np.float64(108.339),
                    "score": np.float64(0.531),
                },
                {
                    "word": "écoute.",
                    "start": np.float64(108.379),
                    "end": np.float64(109.56),
                    "score": np.float64(0.567),
                },
            ],
        },
        {
            "start": 109.6,
            "end": 110.201,
            "text": "Advertising.",
            "words": [
                {
                    "word": "Advertising.",
                    "start": np.float64(109.6),
                    "end": np.float64(110.201),
                    "score": np.float64(0.702),
                }
            ],
        },
        {
            "start": 112.253,
            "end": 118.101,
            "text": " Vous vous sentez seul dans votre vie et vous aimeriez que ça change.",
            "words": [
                {
                    "word": "Vous",
                    "start": np.float64(112.253),
                    "end": np.float64(112.433),
                    "score": np.float64(0.599),
                },
                {
                    "word": "vous",
                    "start": np.float64(112.473),
                    "end": np.float64(112.593),
                    "score": np.float64(0.774),
                },
                {
                    "word": "sentez",
                    "start": np.float64(112.614),
                    "end": np.float64(112.914),
                    "score": np.float64(0.89),
                },
                {
                    "word": "seul",
                    "start": np.float64(112.954),
                    "end": np.float64(113.154),
                    "score": np.float64(0.974),
                },
                {
                    "word": "dans",
                    "start": np.float64(113.194),
                    "end": np.float64(113.314),
                    "score": np.float64(0.857),
                },
                {
                    "word": "votre",
                    "start": np.float64(113.354),
                    "end": np.float64(113.575),
                    "score": np.float64(0.876),
                },
                {
                    "word": "vie",
                    "start": np.float64(113.615),
                    "end": np.float64(114.536),
                    "score": np.float64(0.942),
                },
                {
                    "word": "et",
                    "start": np.float64(114.596),
                    "end": np.float64(114.716),
                    "score": np.float64(0.82),
                },
                {
                    "word": "vous",
                    "start": np.float64(114.736),
                    "end": np.float64(114.836),
                    "score": np.float64(0.911),
                },
                {
                    "word": "aimeriez",
                    "start": np.float64(114.877),
                    "end": np.float64(115.237),
                    "score": np.float64(0.679),
                },
                {
                    "word": "que",
                    "start": np.float64(115.257),
                    "end": np.float64(115.357),
                    "score": np.float64(0.423),
                },
                {
                    "word": "ça",
                    "start": np.float64(115.377),
                    "end": np.float64(115.517),
                    "score": np.float64(0.694),
                },
                {
                    "word": "change.",
                    "start": np.float64(115.537),
                    "end": np.float64(118.101),
                    "score": np.float64(0.555),
                },
            ],
        },
        {
            "start": 118.121,
            "end": 119.102,
            "text": "J'ai la solution.",
            "words": [
                {
                    "word": "J'ai",
                    "start": np.float64(118.121),
                    "end": np.float64(118.281),
                    "score": np.float64(0.729),
                },
                {
                    "word": "la",
                    "start": np.float64(118.321),
                    "end": np.float64(118.401),
                    "score": np.float64(0.81),
                },
                {
                    "word": "solution.",
                    "start": np.float64(118.421),
                    "end": np.float64(119.102),
                    "score": np.float64(0.651),
                },
            ],
        },
        {
            "start": 119.182,
            "end": 121.325,
            "text": "Al-Qaïda !",
            "words": [
                {
                    "word": "Al-Qaïda",
                    "start": np.float64(119.182),
                    "end": np.float64(121.325),
                    "score": np.float64(0.749),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 121.365,
            "end": 122.727,
            "text": "J'ai Al-Qaïda ?",
            "words": [
                {
                    "word": "J'ai",
                    "start": np.float64(121.365),
                    "end": np.float64(121.485),
                    "score": np.float64(0.247),
                },
                {
                    "word": "Al-Qaïda",
                    "start": np.float64(121.525),
                    "end": np.float64(122.727),
                    "score": np.float64(0.81),
                },
                {"word": "?"},
            ],
        },
        {
            "start": 122.767,
            "end": 123.889,
            "text": "Même l'otage est roi.",
            "words": [
                {
                    "word": "Même",
                    "start": np.float64(122.767),
                    "end": np.float64(122.947),
                    "score": np.float64(0.88),
                },
                {
                    "word": "l'otage",
                    "start": np.float64(122.987),
                    "end": np.float64(123.308),
                    "score": np.float64(0.917),
                },
                {
                    "word": "est",
                    "start": np.float64(123.368),
                    "end": np.float64(123.428),
                    "score": np.float64(0.145),
                },
                {
                    "word": "roi.",
                    "start": np.float64(123.468),
                    "end": np.float64(123.889),
                    "score": np.float64(0.724),
                },
            ],
        },
        {
            "start": 124.089,
            "end": 127.974,
            "text": "Je suis en captivité depuis 600 jours et je passe un très bon moment.",
            "words": [
                {
                    "word": "Je",
                    "start": np.float64(124.089),
                    "end": np.float64(124.209),
                    "score": np.float64(0.552),
                },
                {
                    "word": "suis",
                    "start": np.float64(124.229),
                    "end": np.float64(124.349),
                    "score": np.float64(0.406),
                },
                {
                    "word": "en",
                    "start": np.float64(124.389),
                    "end": np.float64(124.469),
                    "score": np.float64(0.681),
                },
                {
                    "word": "captivité",
                    "start": np.float64(124.489),
                    "end": np.float64(124.99),
                    "score": np.float64(0.882),
                },
                {
                    "word": "depuis",
                    "start": np.float64(125.01),
                    "end": np.float64(125.21),
                    "score": np.float64(0.853),
                },
                {"word": "600"},
                {
                    "word": "jours",
                    "start": np.float64(125.531),
                    "end": np.float64(125.691),
                    "score": np.float64(0.919),
                },
                {
                    "word": "et",
                    "start": np.float64(125.731),
                    "end": np.float64(125.811),
                    "score": np.float64(0.587),
                },
                {
                    "word": "je",
                    "start": np.float64(125.831),
                    "end": np.float64(125.911),
                    "score": np.float64(0.945),
                },
                {
                    "word": "passe",
                    "start": np.float64(125.951),
                    "end": np.float64(126.111),
                    "score": np.float64(0.908),
                },
                {
                    "word": "un",
                    "start": np.float64(126.172),
                    "end": np.float64(126.252),
                    "score": np.float64(0.213),
                },
                {
                    "word": "très",
                    "start": np.float64(126.292),
                    "end": np.float64(126.392),
                    "score": np.float64(0.968),
                },
                {
                    "word": "bon",
                    "start": np.float64(126.432),
                    "end": np.float64(126.572),
                    "score": np.float64(0.917),
                },
                {
                    "word": "moment.",
                    "start": np.float64(126.612),
                    "end": np.float64(127.974),
                    "score": np.float64(0.921),
                },
            ],
        },
        {
            "start": 128.014,
            "end": 129.276,
            "text": "Al-Qaïda !",
            "words": [
                {
                    "word": "Al-Qaïda",
                    "start": np.float64(128.014),
                    "end": np.float64(129.276),
                    "score": np.float64(0.759),
                },
                {"word": "!"},
            ],
        },
        {
            "start": 129.336,
            "end": 130.617,
            "text": "Al-Qaïda, c'est notre dada.",
            "words": [
                {
                    "word": "Al-Qaïda,",
                    "start": np.float64(129.336),
                    "end": np.float64(129.977),
                    "score": np.float64(0.724),
                },
                {
                    "word": "c'est",
                    "start": np.float64(129.997),
                    "end": np.float64(130.137),
                    "score": np.float64(0.737),
                },
                {
                    "word": "notre",
                    "start": np.float64(130.177),
                    "end": np.float64(130.397),
                    "score": np.float64(0.62),
                },
                {
                    "word": "dada.",
                    "start": np.float64(130.437),
                    "end": np.float64(130.617),
                    "score": np.float64(0.488),
                },
            ],
        },
        {
            "start": 132.685,
            "end": 136.812,
            "text": " C'est nul.",
            "words": [
                {
                    "word": "C'est",
                    "start": np.float64(132.685),
                    "end": np.float64(135.369),
                    "score": np.float64(0.813),
                },
                {
                    "word": "nul.",
                    "start": np.float64(135.87),
                    "end": np.float64(136.812),
                    "score": np.float64(0.78),
                },
            ],
        },
        {
            "start": 136.832,
            "end": 139.015,
            "text": "1, 2, 3, Al-Qaïda.",
            "words": [
                {"word": "1,"},
                {"word": "2,"},
                {"word": "3,"},
                {
                    "word": "Al-Qaïda.",
                    "start": np.float64(136.912),
                    "end": np.float64(139.015),
                    "score": np.float64(0.491),
                },
            ],
        },
        {
            "start": 139.035,
            "end": 139.797,
            "text": "1, 2, 3, Al-Qaïda.",
            "words": [
                {"word": "1,"},
                {"word": "2,"},
                {"word": "3,"},
                {
                    "word": "Al-Qaïda.",
                    "start": np.float64(139.476),
                    "end": np.float64(139.797),
                    "score": np.float64(0.365),
                },
            ],
        },
        {
            "start": 139.817,
            "end": 141.099,
            "text": "C'est de la merde, les gars.",
            "words": [
                {
                    "word": "C'est",
                    "start": np.float64(139.817),
                    "end": np.float64(139.917),
                    "score": np.float64(0.153),
                },
                {
                    "word": "de",
                    "start": np.float64(139.937),
                    "end": np.float64(140.037),
                    "score": np.float64(0.335),
                },
                {
                    "word": "la",
                    "start": np.float64(140.057),
                    "end": np.float64(140.157),
                    "score": np.float64(0.358),
                },
                {
                    "word": "merde,",
                    "start": np.float64(140.177),
                    "end": np.float64(140.398),
                    "score": np.float64(0.48),
                },
                {
                    "word": "les",
                    "start": np.float64(140.418),
                    "end": np.float64(140.518),
                    "score": np.float64(0.401),
                },
                {
                    "word": "gars.",
                    "start": np.float64(140.538),
                    "end": np.float64(141.099),
                    "score": np.float64(0.754),
                },
            ],
        },
        {
            "start": 141.139,
            "end": 141.66,
            "text": "Hervé, coupe ça.",
            "words": [
                {
                    "word": "Hervé,",
                    "start": np.float64(141.139),
                    "end": np.float64(141.379),
                    "score": np.float64(0.554),
                },
                {
                    "word": "coupe",
                    "start": np.float64(141.399),
                    "end": np.float64(141.56),
                    "score": np.float64(0.676),
                },
                {
                    "word": "ça.",
                    "start": np.float64(141.58),
                    "end": np.float64(141.66),
                    "score": np.float64(0.546),
                },
            ],
        },
        {
            "start": 141.7,
            "end": 142.982,
            "text": "En plus, on n'est pas en rythme.",
            "words": [
                {
                    "word": "En",
                    "start": np.float64(141.7),
                    "end": np.float64(141.74),
                    "score": np.float64(0.785),
                },
                {
                    "word": "plus,",
                    "start": np.float64(141.76),
                    "end": np.float64(141.88),
                    "score": np.float64(0.469),
                },
                {
                    "word": "on",
                    "start": np.float64(141.92),
                    "end": np.float64(141.98),
                    "score": np.float64(0.012),
                },
                {
                    "word": "n'est",
                    "start": np.float64(142.0),
                    "end": np.float64(142.08),
                    "score": np.float64(0.02),
                },
                {
                    "word": "pas",
                    "start": np.float64(142.1),
                    "end": np.float64(142.181),
                    "score": np.float64(0.821),
                },
                {
                    "word": "en",
                    "start": np.float64(142.201),
                    "end": np.float64(142.261),
                    "score": np.float64(0.948),
                },
                {
                    "word": "rythme.",
                    "start": np.float64(142.281),
                    "end": np.float64(142.982),
                    "score": np.float64(0.859),
                },
            ],
        },
        {
            "start": 143.022,
            "end": 145.646,
            "text": "On a dit 5, 6, 4, Al-Qaïda.",
            "words": [
                {
                    "word": "On",
                    "start": np.float64(143.022),
                    "end": np.float64(143.102),
                    "score": np.float64(0.722),
                },
                {
                    "word": "a",
                    "start": np.float64(143.142),
                    "end": np.float64(143.202),
                    "score": np.float64(0.637),
                },
                {
                    "word": "dit",
                    "start": np.float64(143.222),
                    "end": np.float64(143.383),
                    "score": np.float64(0.921),
                },
                {"word": "5,"},
                {"word": "6,"},
                {"word": "4,"},
                {
                    "word": "Al-Qaïda.",
                    "start": np.float64(144.464),
                    "end": np.float64(145.646),
                    "score": np.float64(0.809),
                },
            ],
        },
        {
            "start": 145.686,
            "end": 146.508,
            "text": "C'est pas compliqué, merde.",
            "words": [
                {
                    "word": "C'est",
                    "start": np.float64(145.686),
                    "end": np.float64(145.786),
                    "score": np.float64(0.189),
                },
                {
                    "word": "pas",
                    "start": np.float64(145.807),
                    "end": np.float64(145.887),
                    "score": np.float64(0.841),
                },
                {
                    "word": "compliqué,",
                    "start": np.float64(145.927),
                    "end": np.float64(146.287),
                    "score": np.float64(0.81),
                },
                {
                    "word": "merde.",
                    "start": np.float64(146.327),
                    "end": np.float64(146.508),
                    "score": np.float64(0.719),
                },
            ],
        },
    ]

    return palma, "fr"
    """
