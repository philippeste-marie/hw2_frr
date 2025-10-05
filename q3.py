import re
import os
import pandas as pd
from tqdm import tqdm
from q2 import download_audio, cut_audio
from typing import List


def filter_df(csv_path: str, label: str) -> List[str]:
    """
    Écrivez une fonction qui prend le path vers le csv traité (dans la partie notebook de q1) et renvoie un df avec seulement les rangées qui contiennent l'étiquette `label`.

    Par exemple:
    get_ids("audio_segments_clean.csv", "Speech") ne doit renvoyer que les lignes où l'un des libellés est "Speech"
    """
    # TODO
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"The file {csv_path} does not exist.")
    df = pd.read_csv(csv_path)
    filtered_df = df[df['labels'].str.contains(label, na=False)]
    return filtered_df
    pass


def data_pipeline(csv_path: str, label: str) -> None:
    """
    En utilisant vos fonctions précédemment créées, écrivez une fonction qui prend un csv traité et pour chaque vidéo avec l'étiquette donnée:
    1. Le télécharge à <label>_raw/<ID>.mp3
    2. Le coupe au segment approprié
    3. L'enregistre dans <label>_cut/<ID>.mp3
    (n'oubliez pas de créer le dossier audio/ et le dossier label associé !).

    Il est recommandé d'itérer sur les rangées de filter_df().
    Utilisez tqdm pour suivre la progression du processus de téléchargement (https://tqdm.github.io/)

    Malheureusement, il est possible que certaines vidéos ne peuvent pas être téléchargées. Dans de tels cas, votre pipeline doit gérer l'échec en passant à la vidéo suivante avec l'étiquette.
    """
    # TODO
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"The file {csv_path} does not exist.")
    df = filter_df(csv_path, label)
    for index, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing videos"):
        ytid = row['YTID']
        start = row['start_seconds']
        end = row['end_seconds']
        raw_path = os.path.join(f"{label}_raw", f"{ytid}.mp3")
        cut_path = os.path.join(f"{label}_cut", f"{ytid}.mp3")
        os.makedirs(os.path.dirname(raw_path), exist_ok=True)
        os.makedirs(os.path.dirname(cut_path), exist_ok=True)
        try:
            download_audio(ytid, raw_path)
            cut_audio(raw_path, cut_path, start, end)
        except Exception as e:
            print(f"Failed to process {ytid}: {e}")
            continue
    pass


def rename_files(path_cut: str, csv_path: str) -> None:
    """
    Supposons que nous voulons maintenant renommer les fichiers que nous avons téléchargés dans `path_cut` pour inclure les heures de début et de fin ainsi que la longueur du segment. Alors que
    cela aurait pu être fait dans la fonction data_pipeline(), supposons que nous avons oublié et que nous ne voulons pas tout télécharger à nouveau.

    Écrivez une fonction qui, en utilisant regex (c'est-à-dire la bibliothèque `re`), renomme les fichiers existants de "<ID>.mp3" -> "<ID>_<start_seconds_int>_<end_seconds_int>_<length_int>.mp3"
    dans path_cut. csv_path est le chemin vers le csv traité à partir de q1. `path_cut` est un chemin vers le dossier avec l'audio coupé.

    Par exemple
    "--BfvyPmVMo.mp3" -> "--BfvyPmVMo_20_30_10.mp3"

    ## ATTENTION : supposez que l'YTID peut contenir des caractères spéciaux tels que '.' ou même '.mp3' ##
    """
    # TODO
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"The file {csv_path} does not exist.")
    df = pd.read_csv(csv_path)
    for filename in os.listdir(path_cut):
        if filename.endswith(".mp3"):
            ytid = filename[:-4]  # Remove .mp3 extension
            match = df[df['YTID'] == ytid]
            if not match.empty:
                start = int(match['start_seconds'].values[0])
                end = int(match['end_seconds'].values[0])
                length = end - start
                new_filename = f"{ytid}_{start}_{end}_{length}.mp3"
                os.rename(os.path.join(path_cut, filename), os.path.join(path_cut, new_filename))
    pass


if __name__ == "__main__":
    print(filter_df("audio_segments_clean.csv", "Laughter"))
    data_pipeline("audio_segments_clean.csv", "Laughter")
    rename_files("Laughter_cut", "audio_segments_clean.csv")
