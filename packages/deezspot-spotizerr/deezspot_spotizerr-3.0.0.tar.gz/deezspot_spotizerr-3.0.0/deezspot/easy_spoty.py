#!/usr/bin/python3

from librespot.core import Session, SearchManager
from librespot.metadata import TrackId, AlbumId, ArtistId, EpisodeId, ShowId, PlaylistId
from deezspot.exceptions import InvalidLink
from typing import Any, Dict, List, Optional

# Note: We intentionally avoid importing spotipy. This module is now a
# thin shim over librespot's internal API, returning Web-API-shaped dicts
# consumed by spotloader's converters.

class Spo:
    __error_codes = [404, 400]

    # Class-level references
    __session: Optional[Session] = None
    __initialized = False

    @classmethod
    def set_session(cls, session: Session):
        """Attach an active librespot Session for metadata/search operations."""
        cls.__session = session
        cls.__initialized = True

    @classmethod
    def __init__(cls, client_id=None, client_secret=None):
        """Kept for compatibility; no longer used (librespot session is used)."""
        cls.__initialized = True

    @classmethod
    def __check_initialized(cls):
        if not cls.__initialized or cls.__session is None:
            raise ValueError("Spotify session not initialized. Ensure SpoLogin created a librespot Session and called Spo.set_session(session).")

    # ------------------------- helpers -------------------------
    @staticmethod
    def __base62_from_gid(gid_bytes: bytes, kind: str) -> Optional[str]:
        if not gid_bytes:
            return None
        hex_id = gid_bytes.hex()
        try:
            if kind == 'track':
                obj = TrackId.from_hex(hex_id)
            elif kind == 'album':
                obj = AlbumId.from_hex(hex_id)
            elif kind == 'artist':
                obj = ArtistId.from_hex(hex_id)
            elif kind == 'episode':
                obj = EpisodeId.from_hex(hex_id)
            elif kind == 'show':
                obj = ShowId.from_hex(hex_id)
            elif kind == 'playlist':
                # PlaylistId typically not hex-backed in same way, avoid for playlists here
                return None
            else:
                return None
            uri = obj.to_spotify_uri()
            return uri.split(":")[-1]
        except Exception:
            return None

    @staticmethod
    def __external_ids_to_dict(external_ids) -> Dict[str, str]:
        # Map repeated ExternalId { type, id } to a simple dict
        result: Dict[str, str] = {}
        try:
            for ext in external_ids or []:
                t = getattr(ext, 'type', None)
                v = getattr(ext, 'id', None)
                if t and v:
                    result[t.lower()] = v
        except Exception:
            pass
        return result

    @staticmethod
    def __images_from_group(img_group) -> List[Dict[str, Any]]:
        images: List[Dict[str, Any]] = []
        try:
            for im in getattr(img_group, 'image', []) or []:
                fid = getattr(im, 'file_id', None)
                if fid:
                    hex_id = fid.hex()
                    images.append({
                        'url': f"https://i.scdn.co/image/{hex_id}",
                        'width': getattr(im, 'width', 0),
                        'height': getattr(im, 'height', 0)
                    })
        except Exception:
            pass
        return images

    @staticmethod
    def __images_from_repeated(imgs) -> List[Dict[str, Any]]:
        images: List[Dict[str, Any]] = []
        try:
            for im in imgs or []:
                fid = getattr(im, 'file_id', None)
                if fid:
                    hex_id = fid.hex()
                    images.append({
                        'url': f"https://i.scdn.co/image/{hex_id}",
                        'width': getattr(im, 'width', 0),
                        'height': getattr(im, 'height', 0)
                    })
        except Exception:
            pass
        return images

    @classmethod
    def __artist_proto_to_dict(cls, a_proto) -> Dict[str, Any]:
        gid = getattr(a_proto, 'gid', None)
        return {
            'id': cls.__base62_from_gid(gid, 'artist'),
            'name': getattr(a_proto, 'name', '')
        }

    @classmethod
    def __track_proto_to_web_dict(cls, t_proto, parent_album: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        if t_proto is None:
            return {}
        gid = getattr(t_proto, 'gid', None)
        artists = [cls.__artist_proto_to_dict(a) for a in getattr(t_proto, 'artist', [])]
        external_ids_map = cls.__external_ids_to_dict(getattr(t_proto, 'external_id', []))
        # Album for a track inside Album.disc.track is often simplified in proto
        album_dict = parent_album or {}
        return {
            'id': cls.__base62_from_gid(gid, 'track'),
            'name': getattr(t_proto, 'name', ''),
            'duration_ms': getattr(t_proto, 'duration', 0),
            'explicit': getattr(t_proto, 'explicit', False),
            'track_number': getattr(t_proto, 'number', 1),
            'disc_number': getattr(t_proto, 'disc_number', 1),
            'artists': artists,
            'external_ids': external_ids_map,
            'available_markets': None,  # Not derived; market check code handles None by warning and continuing
            'album': album_dict
        }

    @classmethod
    def __album_proto_to_web_dict(cls, a_proto) -> Dict[str, Any]:
        if a_proto is None:
            return {}
        gid = getattr(a_proto, 'gid', None)
        # Album basic fields
        title = getattr(a_proto, 'name', '')
        album_type = None
        try:
            # Map enum to typical Web API strings when possible
            t_val = getattr(a_proto, 'type', None)
            if t_val is not None:
                # Common mapping heuristic
                # 1 = ALBUM, 2 = SINGLE, 3 = COMPILATION (values may differ by proto)
                mapping = {1: 'album', 2: 'single', 3: 'compilation'}
                album_type = mapping.get(int(t_val), None)
        except Exception:
            album_type = None

        # Date
        release_date_str = ''
        release_date_precision = 'day'
        try:
            date = getattr(a_proto, 'date', None)
            year = getattr(date, 'year', 0) if date else 0
            month = getattr(date, 'month', 0) if date else 0
            day = getattr(date, 'day', 0) if date else 0
            if year and month and day:
                release_date_str = f"{year:04d}-{month:02d}-{day:02d}"
                release_date_precision = 'day'
            elif year and month:
                release_date_str = f"{year:04d}-{month:02d}"
                release_date_precision = 'month'
            elif year:
                release_date_str = f"{year:04d}"
                release_date_precision = 'year'
        except Exception:
            pass

        # Artists
        artists = [cls.__artist_proto_to_dict(a) for a in getattr(a_proto, 'artist', [])]

        # Genres
        genres = list(getattr(a_proto, 'genre', []) or [])

        # External IDs (e.g., upc)
        external_ids_map = cls.__external_ids_to_dict(getattr(a_proto, 'external_id', []))

        # Images
        images: List[Dict[str, Any]] = []
        try:
            cg = getattr(a_proto, 'cover_group', None)
            if cg:
                images = cls.__images_from_group(cg)
            if not images:
                images = cls.__images_from_repeated(getattr(a_proto, 'cover', []) or [])
        except Exception:
            images = []

        # Tracks from discs
        items: List[Dict[str, Any]] = []
        total_tracks = 0
        try:
            for disc in getattr(a_proto, 'disc', []) or []:
                disc_number = getattr(disc, 'number', 1)
                for t in getattr(disc, 'track', []) or []:
                    total_tracks += 1
                    # Album context passed minimally for track mapper
                    parent_album_min = {
                        'id': cls.__base62_from_gid(gid, 'album'),
                        'name': title,
                        'album_type': album_type,
                        'release_date': release_date_str,
                        'release_date_precision': release_date_precision,
                        'total_tracks': None,
                        'images': images,
                        'genres': genres,
                        'artists': artists,
                        'external_ids': external_ids_map,
                        'available_markets': None
                    }
                    # Ensure numbering aligns with album context
                    setattr(t, 'disc_number', disc_number)
                    item = cls.__track_proto_to_web_dict(t, parent_album=parent_album_min)
                    # Override with correct numbering if proto uses different fields
                    item['disc_number'] = disc_number
                    if 'track_number' not in item or not item['track_number']:
                        item['track_number'] = getattr(t, 'number', 1)
                    items.append(item)
        except Exception:
            items = []

        album_dict: Dict[str, Any] = {
            'id': cls.__base62_from_gid(gid, 'album'),
            'name': title,
            'album_type': album_type,
            'release_date': release_date_str,
            'release_date_precision': release_date_precision,
            'total_tracks': total_tracks or getattr(a_proto, 'num_tracks', 0),
            'genres': genres,
            'images': images,  # Web API-like images with i.scdn.co URLs
            'copyrights': [],
            'available_markets': None,
            'external_ids': external_ids_map,
            'artists': artists,
            'tracks': {
                'items': items,
                'total': len(items),
                'limit': len(items),
                'offset': 0,
                'next': None,
                'previous': None
            }
        }
        return album_dict

    # ------------------------- public API -------------------------
    @classmethod
    def get_track(cls, ids, client_id=None, client_secret=None):
        cls.__check_initialized()
        try:
            t_id = TrackId.from_base62(ids)
            t_proto = cls.__session.api().get_metadata_4_track(t_id)
            if not t_proto:
                raise InvalidLink(ids)
            # Build minimal album context from nested album proto if present
            album_proto = getattr(t_proto, 'album', None)
            album_ctx = None
            try:
                if album_proto is not None:
                    agid = getattr(album_proto, 'gid', None)
                    # Images for embedded album
                    images: List[Dict[str, Any]] = []
                    try:
                        cg = getattr(album_proto, 'cover_group', None)
                        if cg:
                            images = cls.__images_from_group(cg)
                        if not images:
                            images = cls.__images_from_repeated(getattr(album_proto, 'cover', []) or [])
                    except Exception:
                        images = []
                    album_ctx = {
                        'id': cls.__base62_from_gid(agid, 'album'),
                        'name': getattr(album_proto, 'name', ''),
                        'images': images,
                        'genres': [],
                        'available_markets': None
                    }
            except Exception:
                album_ctx = None
            return cls.__track_proto_to_web_dict(t_proto, parent_album=album_ctx)
        except InvalidLink:
            raise
        except Exception:
            raise InvalidLink(ids)

    @classmethod
    def get_tracks(cls, ids: list, market: str = None, client_id=None, client_secret=None):
        if not ids:
            return {'tracks': []}
        cls.__check_initialized()
        tracks: List[Dict[str, Any]] = []
        for tid in ids:
            try:
                tracks.append(cls.get_track(tid))
            except Exception:
                # Preserve order with None entries similar to Web API behavior on bad IDs
                tracks.append(None)
        return {'tracks': tracks}

    @classmethod
    def get_album(cls, ids, client_id=None, client_secret=None):
        cls.__check_initialized()
        try:
            a_id = AlbumId.from_base62(ids)
            a_proto = cls.__session.api().get_metadata_4_album(a_id)
            if not a_proto:
                raise InvalidLink(ids)
            return cls.__album_proto_to_web_dict(a_proto)
        except InvalidLink:
            raise
        except Exception:
            raise InvalidLink(ids)

    @classmethod
    def get_playlist(cls, ids, client_id=None, client_secret=None):
        cls.__check_initialized()
        try:
            # PlaylistId accepts base62-ish/id string directly
            p_id = PlaylistId(ids)
            p_proto = cls.__session.api().get_playlist(p_id)
            if not p_proto:
                raise InvalidLink(ids)
            # Minimal mapping sufficient for current playlist flow
            name = None
            try:
                attrs = getattr(p_proto, 'attributes', None)
                name = getattr(attrs, 'name', None) if attrs else None
            except Exception:
                name = None
            owner_name = getattr(p_proto, 'owner_username', None) or 'Unknown Owner'
            items = []
            try:
                contents = getattr(p_proto, 'contents', None)
                for it in getattr(contents, 'items', []) or []:
                    # Attempt to obtain a track gid/id from multiple potential locations
                    tref = getattr(it, 'track', None)
                    gid = getattr(tref, 'gid', None) if tref else None
                    base62 = cls.__base62_from_gid(gid, 'track') if gid else None

                    # Some playlists can reference an "original_track" field
                    if not base62:
                        orig = getattr(it, 'original_track', None)
                        ogid = getattr(orig, 'gid', None) if orig else None
                        base62 = cls.__base62_from_gid(ogid, 'track') if ogid else None

                    # As an additional fallback, try to parse a spotify:track: URI if exposed on the nested track
                    if not base62:
                        uri = getattr(tref, 'uri', None) if tref else None
                        if isinstance(uri, str) and uri.startswith("spotify:track:"):
                            try:
                                parts = uri.split(":")
                                maybe_id = parts[-1] if parts else None
                                if maybe_id and len(maybe_id) == 22:
                                    base62 = maybe_id
                                elif maybe_id and len(maybe_id) in (32, 40):
                                    from librespot.metadata import TrackId
                                    tid = TrackId.from_hex(maybe_id)
                                    base62 = tid.to_spotify_uri().split(":")[-1]
                            except Exception:
                                base62 = None

                    # Fallback: some implementations expose the URI at the item level
                    if not base62:
                        item_uri = getattr(it, 'uri', None)
                        if isinstance(item_uri, str) and item_uri.startswith("spotify:track:"):
                            try:
                                parts = item_uri.split(":")
                                maybe_id = parts[-1] if parts else None
                                if maybe_id and len(maybe_id) == 22:
                                    base62 = maybe_id
                                elif maybe_id and len(maybe_id) in (32, 40):
                                    from librespot.metadata import TrackId
                                    tid = TrackId.from_hex(maybe_id)
                                    base62 = tid.to_spotify_uri().split(":")[-1]
                            except Exception:
                                base62 = None

                    # Fallback: check original_track uri if provided
                    if not base62:
                        orig = getattr(it, 'original_track', None)
                        o_uri = getattr(orig, 'uri', None) if orig else None
                        if isinstance(o_uri, str) and o_uri.startswith("spotify:track:"):
                            try:
                                parts = o_uri.split(":")
                                maybe_id = parts[-1] if parts else None
                                if maybe_id and len(maybe_id) == 22:
                                    base62 = maybe_id
                                elif maybe_id and len(maybe_id) in (32, 40):
                                    from librespot.metadata import TrackId
                                    tid = TrackId.from_hex(maybe_id)
                                    base62 = tid.to_spotify_uri().split(":")[-1]
                            except Exception:
                                base62 = None

                    if base62:
                        items.append({'track': {'id': base62}})
            except Exception:
                items = []
            return {
                'name': name or 'Unknown Playlist',
                'owner': {'display_name': owner_name},
                'images': [],
                'tracks': {'items': items, 'total': len(items)}
            }
        except InvalidLink:
            raise
        except Exception:
            raise InvalidLink(ids)

    @classmethod
    def get_episode(cls, ids, client_id=None, client_secret=None):
        cls.__check_initialized()
        try:
            e_id = EpisodeId.from_base62(ids)
            e_proto = cls.__session.api().get_metadata_4_episode(e_id)
            if not e_proto:
                raise InvalidLink(ids)
            # Map show info
            show_proto = getattr(e_proto, 'show', None)
            show_id = None
            show_name = ''
            publisher = ''
            try:
                sgid = getattr(show_proto, 'gid', None) if show_proto else None
                show_id = cls.__base62_from_gid(sgid, 'show') if sgid else None
                show_name = getattr(show_proto, 'name', '') if show_proto else ''
                publisher = getattr(show_proto, 'publisher', '') if show_proto else ''
            except Exception:
                pass
            # Images for episode (cover_image ImageGroup)
            images: List[Dict[str, Any]] = []
            try:
                images = cls.__images_from_group(getattr(e_proto, 'cover_image', None))
            except Exception:
                images = []
            return {
                'id': cls.__base62_from_gid(getattr(e_proto, 'gid', None), 'episode'),
                'name': getattr(e_proto, 'name', ''),
                'duration_ms': getattr(e_proto, 'duration', 0),
                'explicit': getattr(e_proto, 'explicit', False),
                'images': images,
                'available_markets': None,
                'show': {
                    'id': show_id,
                    'name': show_name,
                    'publisher': publisher
                }
            }
        except InvalidLink:
            raise
        except Exception:
            raise InvalidLink(ids)

    @classmethod
    def get_artist(cls, ids, album_type='album,single,compilation,appears_on', limit: int = 50, client_id=None, client_secret=None):
        """Return a dict with artist name and an 'items' list of albums matching album_type.
        Each item contains an external_urls.spotify link, minimally enough for download_artist."""
        cls.__check_initialized()
        try:
            ar_id = ArtistId.from_base62(ids)
            ar_proto = cls.__session.api().get_metadata_4_artist(ar_id)
            if not ar_proto:
                raise InvalidLink(ids)
            # Parse requested groups
            requested = [s.strip().lower() for s in str(album_type).split(',') if s.strip()]
            order = ['album', 'single', 'compilation', 'appears_on']
            items: List[Dict[str, Any]] = []
            for group_name in order:
                if requested and group_name not in requested:
                    continue
                attr = f"{group_name}_group"
                grp = getattr(ar_proto, attr, None)
                if not grp:
                    continue
                # grp is repeated AlbumGroup; each has 'album' repeated Album
                try:
                    for ag in grp:
                        albums = getattr(ag, 'album', []) or []
                        for a in albums:
                            gid = getattr(a, 'gid', None)
                            base62 = cls.__base62_from_gid(gid, 'album') if gid else None
                            name = getattr(a, 'name', '')
                            if base62:
                                items.append({
                                    'name': name,
                                    'external_urls': {'spotify': f"https://open.spotify.com/album/{base62}"}
                                })
                            if limit and len(items) >= int(limit):
                                break
                        if limit and len(items) >= int(limit):
                            break
                except Exception:
                    continue
                if limit and len(items) >= int(limit):
                    break
            return {
                'id': cls.__base62_from_gid(getattr(ar_proto, 'gid', None), 'artist'),
                'name': getattr(ar_proto, 'name', ''),
                'items': items
            }
        except InvalidLink:
            raise
        except Exception:
            raise InvalidLink(ids)

    # ------------------------- search (optional) -------------------------
    @classmethod
    def __get_session_country_code(cls) -> str:
        try:
            if cls.__session is None:
                return ""
            cc = getattr(cls.__session, "_Session__country_code", None)
            if isinstance(cc, str) and len(cc) == 2:
                return cc
            cc2 = getattr(cls.__session, "country_code", None)
            if isinstance(cc2, str) and len(cc2) == 2:
                return cc2
        except Exception:
            pass
        return ""

    @classmethod
    def search(cls, query, search_type='track', limit=10, country: Optional[str] = None, locale: Optional[str] = None, catalogue: Optional[str] = None, image_size: Optional[str] = None, client_id=None, client_secret=None):
        cls.__check_initialized()
        # Map simple type value; librespot returns a combined JSON-like response
        req = SearchManager.SearchRequest(query).set_limit(limit)
        # Country precedence: explicit country > session country
        if country:
            req.set_country(country)
        else:
            cc = cls.__get_session_country_code()
            if cc:
                req.set_country(cc)
        if locale:
            req.set_locale(locale)
        if catalogue:
            req.set_catalogue(catalogue)
        if image_size:
            req.set_image_size(image_size)
        res = cls.__session.search().request(req)
        return res
