import hashlib
import json
from dataclasses import asdict
from pathlib import Path
from typing import Optional, Dict, List
from entita.user import User


class GestioneUser:
    def __init__(self, filepath: str = "data/users.json"):
        self.filepath = Path(filepath)
        self.filepath.parent.mkdir(parents=True, exist_ok=True)
        self._users: Dict[str, User] = {}
        self.carica()

    def carica(self):
        """Carica gli utenti dal file JSON. Se non esiste, crea gli utenti iniziali."""
        if not self.filepath.exists():
            self._users = {
                "admin": User(
                    username="admin",
                    password=self._hash_password("admin1234"),
                    ruolo="amministratore",
                    matricola="",
                    primo_accesso=False
                ),
                "101": User(
                    username="101",
                    password=self._hash_password("operaio1234"),
                    ruolo="operaio",
                    matricola="101",
                    primo_accesso=True
                )
            }
            self.salva()
            return

        with open(self.filepath, "r", encoding="utf-8") as f:
            dati = json.load(f)
            self._users = {d["username"]: User(**d) for d in dati}

    def salva(self):
        """Salva tutti gli utenti su file JSON."""
        dati_da_salvare = [asdict(u) for u in self._users.values()]
        with open(self.filepath, "w", encoding="utf-8") as f:
            json.dump(dati_da_salvare, f, indent=2, ensure_ascii=False)

    @staticmethod
    def _hash_password(password: str) -> str:
        return hashlib.sha256(password.encode('utf-8')).hexdigest()

    @staticmethod
    def valida_password(password: str) -> bool:
        """Requisito RNF3: La password deve contenere almeno 8 caratteri."""
        return len(password) >= 8

    def get_tutti(self) -> List[User]:
        return list(self._users.values())

    def get_matricole_associate(self) -> set:
        """Restituisce l'insieme delle matricole già associate a uno User."""
        return {u.matricola for u in self._users.values() if u.matricola}

    def autentica(self, username: str, password_in_chiaro: str) -> Optional[User]:
        """Requisito RF29: Autenticazione utente."""
        username = username.strip()
        user = self._users.get(username)
        if user is None:
            return None
        if user.password == self._hash_password(password_in_chiaro):
            return user
        return None

    def aggiungi_user(self, user: User) -> bool:
        """Requisito RF27: Inserimento di uno User e salvataggio."""
        if user.username in self._users:
            return False
        user.password = self._hash_password(user.password)
        self._users[user.username] = user
        self.salva()
        return True

    def cambia_password(self, username: str, vecchia_pass: str, nuova_pass: str) -> bool:
        """Requisito RF26: Reimpostazione Password e salvataggio."""
        user = self._users.get(username)
        if user is None:
            return False
        if user.password != self._hash_password(vecchia_pass):
            return False
        if not self.valida_password(nuova_pass):
            return False

        user.password = self._hash_password(nuova_pass)
        user.primo_accesso = False
        self.salva()
        return True

    def ricerca_user(self, username: str) -> Optional[User]:
        """Requisito RF28: Ricerca User."""
        return self._users.get(username)

    def modifica_user(self, user_aggiornato: User, nuova_password_in_chiaro: str = "") -> bool:
        """Requisito RF27: Modifica di uno User esistente e salvataggio."""
        if user_aggiornato.username not in self._users:
            return False

        user_esistente = self._users[user_aggiornato.username]
        if nuova_password_in_chiaro:
            user_aggiornato.password = self._hash_password(nuova_password_in_chiaro)
        else:
            # Mantiene l'hash della password attuale
            user_aggiornato.password = user_esistente.password

        self._users[user_aggiornato.username] = user_aggiornato
        self.salva()
        return True

    def rimuovi_user(self, username: str) -> bool:
        """Requisito RF27: Rimozione di uno User e salvataggio."""
        if username in self._users:
            del self._users[username]
            self.salva()
            return True
        return False