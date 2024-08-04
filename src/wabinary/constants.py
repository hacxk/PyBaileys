


# Constants for each hostname's information
MEDIA_FCMB6_1_FNA = {
    "hostname": "media.fcmb6-1.fna.whatsapp.net",
    "class": "fna",
    "ips": [
        {
            "ip4": "223.224.4.34",
            "ip6": "2400:ff00:2:0:face:b00c:3333:7020"
        }
    ],
    "fallback": {
        "hostname": "media.fcmb12-1.fna.whatsapp.net",
        "class": "fna",
        "ips": [
            {
                "ip4": "223.224.4.161",
                "ip6": "2400:ff00:5:0:face:b00c:3333:7020"
            }
        ]
    },
    "type": "primary",
    "rules": [
        {
            "download": [
                "video", "image", "gif", "sticker", "newsletter-image", "newsletter-video", "newsletter-thumbnail-link",
                "newsletter-sticker", "newsletter-document", "newsletter-gif", "newsletter-ptt", "newsletter-audio",
                "thumbnail-image", "thumbnail-video"
            ]
        },
        {
            "downloadBuckets": ["0"]
        }
    ]
    }

MEDIA_BOM1_1_CDN = {
    "hostname": "media-bom1-1.cdn.whatsapp.net",
    "class": "pop",
    "ips": [
        {
            "ip4": "157.240.16.52",
            "ip6": "2a03:2880:f22f:c5:face:b00c:0:167"
        }
    ],
    "fallback": {
        "hostname": "media-sin6-3.cdn.whatsapp.net",
        "class": "pop",
        "ips": [
            {
                "ip4": "157.240.15.60",
                "ip6": "2a03:2880:f20c:1c2:face:b00c:0:167"
            }
        ]
    },
    "type": "primary",
    "rules": [
        {
            "download": [
                "ppic", "md-app-state", "thumbnail-document", "biz-cover-photo", "ptt", "audio", "document",
                "thumbnail-link", "md-msg-hist"
            ]
        },
        {
            "downloadBuckets": ["0"]
        }
    ]
}

MEDIA_BOM1_2_CDN = {
    "hostname": "media-bom1-2.cdn.whatsapp.net",
    "class": "pop",
    "ips": [
        {
            "ip4": "31.13.79.53",
            "ip6": "2a03:2880:f22f:1c6:face:b00c:0:167"
        }
    ],
    "fallback": {
        "hostname": "media-sin6-2.cdn.whatsapp.net",
        "class": "pop",
        "ips": [
            {
                "ip4": "157.240.13.54",
                "ip6": "2a03:2880:f20c:2c6:face:b00c:0:167"
            }
        ]
    },
    "type": "primary",
    "rules": [
        {
            "upload": [
                "image", "sticker", "ptt", "audio", "document", "video", "gif", "ppic", "md-app-state", "md-msg-hist",
                "template", "thumbnail-image", "thumbnail-video", "thumbnail-document", "thumbnail-link", "payment-bg-image",
                "product", "product-catalog-image", "biz-cover-photo", "preview", "newsletter-audio", "newsletter-document",
                "newsletter-image", "newsletter-gif", "newsletter-ptt", "newsletter-sticker", "newsletter-thumbnail-link",
                "newsletter-video"
            ]
        }
    ]
}

MMG_WHATSAPP_NET = {
    "hostname": "mmg.whatsapp.net",
    "class": "pop",
    "ips": [{}],
    "type": "fallback",
    "rules": [
        {
            "download": [
                "image", "sticker", "ptt", "audio", "document", "video", "gif", "ppic", "md-app-state", "md-msg-hist",
                "template", "thumbnail-image", "thumbnail-video", "thumbnail-document", "thumbnail-link", "payment-bg-image",
                "product", "product-catalog-image", "biz-cover-photo", "preview", "newsletter-audio", "newsletter-document",
                "newsletter-image", "newsletter-gif", "newsletter-ptt", "newsletter-sticker", "newsletter-thumbnail-link",
                "newsletter-video"
            ]
        },
        {
            "upload": [
                "image", "sticker", "ptt", "audio", "document", "video", "gif", "ppic", "md-app-state", "md-msg-hist",
                "template", "thumbnail-image", "thumbnail-video", "thumbnail-document", "thumbnail-link", "payment-bg-image",
                "product", "product-catalog-image", "biz-cover-photo", "preview", "newsletter-audio", "newsletter-document",
                "newsletter-image", "newsletter-gif", "newsletter-ptt", "newsletter-sticker", "newsletter-thumbnail-link",
                "newsletter-video"
            ]
        }
    ]
}

# Aggregate all hosts
WAMMS4_CONN = {
    "hosts": [
        MEDIA_FCMB6_1_FNA,
        MEDIA_BOM1_1_CDN,
        MEDIA_BOM1_2_CDN,
        MMG_WHATSAPP_NET
    ],
    "ttl": 300000,
    "maxBuckets": 12,
    "authTTL": 21600000
}


class BinaryNodeCodingOptions:
    TAGS = {
        'LIST_EMPTY': 0,
        'DICTIONARY_0': 236,
        'DICTIONARY_1': 237,
        'DICTIONARY_2': 238,
        'DICTIONARY_3': 239,
        'AD_JID': 247,
        'LIST_8': 248,
        'LIST_16': 249,
        'JID_PAIR': 250,
        'HEX_8': 251,
        'BINARY_8': 252,
        'BINARY_20': 253,
        'BINARY_32': 254,
        'NIBBLE_8': 255,
        'PACKED_MAX': 127,
        'SINGLE_BYTE_MAX': 256,
        'STREAM_END': 2
    }

    SINGLE_BYTE_TOKENS = [
        '', 'xmlstreamstart', 'xmlstreamend', 's.whatsapp.net', 'type', 'participant', 'from', 'receipt', 'id', 'broadcast', 'status', 'message', 'notification', 'notify', 'to', 'jid', 'user', 'class', 'offline', 'g.us', 'result', 'mediatype', 'enc', 'skmsg', 'off_cnt', 'xmlns', 'presence', 'participants', 'ack', 't', 'iq', 'device_hash', 'read', 'value', 'media', 'picture', 'chatstate', 'unavailable', 'text', 'urn:xmpp:whatsapp:push', 'devices', 'verified_name', 'contact', 'composing', 'edge_routing', 'routing_info', 'item', 'image', 'verified_level', 'get', 'fallback_hostname', '2', 'media_conn', '1', 'v', 'handshake', 'fallback_class', 'count', 'config', 'offline_preview', 'download_buckets', 'w:profile:picture', 'set', 'creation', 'location', 'fallback_ip4', 'msg', 'urn:xmpp:ping', 'fallback_ip6', 'call-creator', 'relaylatency', 'success', 'subscribe', 'video', 'business_hours_config', 'platform', 'hostname', 'version', 'unknown', '0', 'ping', 'hash', 'edit', 'subject', 'max_buckets', 'download', 'delivery', 'props', 'sticker', 'name', 'last', 'contacts', 'business', 'primary', 'preview', 'w:p', 'pkmsg', 'call-id', 'retry', 'prop', 'call', 'auth_ttl', 'available', 'relay_id', 'last_id', 'day_of_week', 'w', 'host', 'seen', 'bits', 'list', 'atn', 'upload', 'is_new', 'w:stats', 'key', 'paused', 'specific_hours', 'multicast', 'stream:error', 'mmg.whatsapp.net', 'code', 'deny', 'played', 'profile', 'fna', 'device-list', 'close_time', 'latency', 'gcm', 'pop', 'audio', '26', 'w:web', 'open_time', 'error', 'auth', 'ip4', 'update', 'profile_options', 'config_value', 'category', 'catalog_not_created', '00', 'config_code', 'mode', 'catalog_status', 'ip6', 'blocklist', 'registration', '7', 'web', 'fail', 'w:m', 'cart_enabled', 'ttl', 'gif', '300', 'device_orientation', 'identity', 'query', '401', 'media-gig2-1.cdn.whatsapp.net', 'in', '3', 'te2', 'add', 'fallback', 'categories', 'ptt', 'encrypt', 'notice', 'thumbnail-document', 'item-not-found', '12', 'thumbnail-image', 'stage', 'thumbnail-link', 'usync', 'out', 'thumbnail-video', '8', '01', 'context', 'sidelist', 'thumbnail-gif', 'terminate', 'not-authorized', 'orientation', 'dhash', 'capability', 'side_list', 'md-app-state', 'description', 'serial', 'readreceipts', 'te', 'business_hours', 'md-msg-hist', 'tag', 'attribute_padding', 'document', 'open_24h', 'delete', 'expiration', 'active', 'prev_v_id', 'true', 'passive', 'index', '4', 'conflict', 'remove', 'w:gp2', 'config_expo_key', 'screen_height', 'replaced', '02', 'screen_width', 'uploadfieldstat', '2:47DEQpj8', 'media-bog1-1.cdn.whatsapp.net', 'encopt', 'url', 'catalog_exists', 'keygen', 'rate', 'offer', 'opus', 'media-mia3-1.cdn.whatsapp.net', 'privacy', 'media-mia3-2.cdn.whatsapp.net', 'signature', 'preaccept', 'token_id', 'media-eze1-1.cdn.whatsapp.net'
    ]

    # Double Byte Tokens
    DOUBLE_BYTE_TOKENS = [
    [
        'media-for1-1.cdn.whatsapp.net', 'relay', 'media-gru2-2.cdn.whatsapp.net', 'uncompressed', 
        'medium', 'voip_settings', 'device', 'reason', 'media-lim1-1.cdn.whatsapp.net', 
        'media-qro1-2.cdn.whatsapp.net', 'media-gru1-2.cdn.whatsapp.net', 'action', 'features', 
        'media-gru2-1.cdn.whatsapp.net', 'media-gru1-1.cdn.whatsapp.net', 'media-otp1-1.cdn.whatsapp.net', 
        'kyc-id', 'priority', 'phash', 'mute', 'token', '100', 'media-qro1-1.cdn.whatsapp.net', 
        'none', 'media-mrs2-2.cdn.whatsapp.net', 'sign_credential', '03', 'media-mrs2-1.cdn.whatsapp.net', 
        'protocol', 'timezone', 'transport', 'eph_setting', '1080', 'original_dimensions', 
        'media-frx5-1.cdn.whatsapp.net', 'background', 'disable', 'original_image_url', '5', 
        'transaction-id', 'direct_path', '103', 'appointment_only', 'request_image_url', 'peer_pid', 
        'address', '105', '104', '102', 'media-cdt1-1.cdn.whatsapp.net', '101', '109', '110', 
        '106', 'background_location', 'v_id', 'sync', 'status-old', '111', '107', 'ppic', 
        'media-scl2-1.cdn.whatsapp.net', 'business_profile', '108', 'invite', '04', 'audio_duration', 
        'media-mct1-1.cdn.whatsapp.net', 'media-cdg2-1.cdn.whatsapp.net', 'media-los2-1.cdn.whatsapp.net', 
        'invis', 'net', 'voip_payload_type', 'status-revoke-delay', '404', 'state', 
        'use_correct_order_for_hmac_sha1', 'ver', 'media-mad1-1.cdn.whatsapp.net', 'order', '540', 
        'skey', 'blinded_credential', 'android', 'contact_remove', 'enable_downlink_relay_latency_only', 
        'duration', 'enable_vid_one_way_codec_nego', '6', 'media-sof1-1.cdn.whatsapp.net', 'accept', 
        'all', 'signed_credential', 'media-atl3-1.cdn.whatsapp.net', 'media-lhr8-1.cdn.whatsapp.net', 
        'website', '05', 'latitude', 'media-dfw5-1.cdn.whatsapp.net', 'forbidden', 
        'enable_audio_piggyback_network_mtu_fix', 'media-dfw5-2.cdn.whatsapp.net', 'note.m4r', 
        'media-atl3-2.cdn.whatsapp.net', 'jb_nack_discard_count_fix', 'longitude', 'Opening.m4r', 
        'media-arn2-1.cdn.whatsapp.net', 'email', 'timestamp', 'admin', 'media-pmo1-1.cdn.whatsapp.net', 
        'America/Sao_Paulo', 'contact_add', 'media-sin6-1.cdn.whatsapp.net', 'interactive', '8000', 
        'acs_public_key', 'sigquit_anr_detector_release_rollover_percent', 'media.fmed1-2.fna.whatsapp.net', 
        'groupadd', 'enabled_for_video_upgrade', 'latency_update_threshold', 'media-frt3-2.cdn.whatsapp.net', 
        'calls_row_constraint_layout', 'media.fgbb2-1.fna.whatsapp.net', 'mms4_media_retry_notification_encryption_enabled', 
        'timeout', 'media-sin6-3.cdn.whatsapp.net', 'audio_nack_jitter_multiplier', 'jb_discard_count_adjust_pct_rc', 
        'audio_reserve_bps', 'delta', 'account_sync', 'default', 'media.fjed4-6.fna.whatsapp.net', '06', 
        'lock_video_orientation', 'media-frt3-1.cdn.whatsapp.net', 'w:g2', 'media-sin6-2.cdn.whatsapp.net', 
        'audio_nack_algo_mask', 'media.fgbb2-2.fna.whatsapp.net', 'media.fmed1-1.fna.whatsapp.net', 
        'cond_range_target_bitrate', 'mms4_server_error_receipt_encryption_enabled', 'vid_rc_dyn', 'fri', 
        'cart_v1_1_order_message_changes_enabled', 'reg_push', 'jb_hist_deposit_value', 'privatestats', 
        'media.fist7-2.fna.whatsapp.net', 'thu', 'jb_discard_count_adjust_pct', 'mon', 
        'group_call_video_maximization_enabled', 'mms_cat_v1_forward_hot_override_enabled', 'audio_nack_new_rtt', 
        'media.fsub2-3.fna.whatsapp.net', 'media_upload_aggressive_retry_exponential_backoff_enabled', 'tue', 
        'wed', 'media.fruh4-2.fna.whatsapp.net', 'audio_nack_max_seq_req', 'max_rtp_audio_packet_resends', 
        'jb_hist_max_cdf_value', '07', 'audio_nack_max_jb_delay', 'mms_forward_partially_downloaded_video', 
        'media-lcy1-1.cdn.whatsapp.net', 'resume', 'jb_inband_fec_aware', 'new_commerce_entry_point_enabled', 
        '480', 'payments_upi_generate_qr_amount_limit', 'sigquit_anr_detector_rollover_percent', 
        'media.fsdu2-1.fna.whatsapp.net', 'fbns', 'aud_pkt_reorder_pct', 'dec', 
        'stop_probing_before_accept_send', 'media_upload_max_aggressive_retries', 
        'edit_business_profile_new_mode_enabled', 'media.fhex4-1.fna.whatsapp.net', 'media.fjed4-3.fna.whatsapp.net', 
        'sigquit_anr_detector_64bit_rollover_percent', 'cond_range_ema_jb_last_delay', 'watls_enable_early_data_http_get', 
        'media.fsdu2-2.fna.whatsapp.net', 'message_qr_disambiguation_enabled', 'media-mxp1-1.cdn.whatsapp.net', 
        'sat', 'vertical', 'media.fruh4-5.fna.whatsapp.net', '200', 'media-sof1-2.cdn.whatsapp.net', '-1', 
        'height', 'product_catalog_hide_show_items_enabled', 'deep_copy_frm_last', 'tsoffline', 'vp8/h.264', 
        'media.fgye5-3.fna.whatsapp.net', 'media.ftuc1-2.fna.whatsapp.net', 'smb_upsell_chat_banner_enabled', 
        'canonical', '08', '9', '.', 'media.fgyd4-4.fna.whatsapp.net', 'media.fsti4-1.fna.whatsapp.net', 
        'mms_vcache_aggregation_enabled', 'mms_hot_content_timespan_in_seconds', 'nse_ver', 'rte', 
        'third_party_sticker_web_sync', 'cond_range_target_total_bitrate', 'media_upload_aggressive_retry_enabled', 
        'instrument_spam_report_enabled', 'disable_reconnect_tone', 'move_media_folder_from_sister_app', 
        'one_tap_calling_in_group_chat_size', '10', 'storage_mgmt_banner_threshold_mb', 'enable_backup_passive_mode', 
        'sharechat_inline_player_enabled', 'media.fcnq2-1.fna.whatsapp.net', 'media.fhex4-2.fna.whatsapp.net', 
        'media.fist6-3.fna.whatsapp.net', 'ephemeral_drop_column_stage', 'reconnecting_after_network_change_threshold_ms', 
        'media-lhr8-2.cdn.whatsapp.net', 'cond_jb_last_delay_ema_alpha', 'entry_point_block_logging_enabled', 
        'critical_event_upload_log_config', 'respect_initial_bitrate_estimate', 'smaller_image_thumbs_status_enabled', 
        'media.fbtz1-4.fna.whatsapp.net', 'media.fjed4-1.fna.whatsapp.net', 'width', '720', 'enable_frame_dropper', 
        'enable_one_side_mode', 'urn:xmpp:whatsapp:dirty', 'new_sticker_animation_behavior_v2', 
        'media.flim3-2.fna.whatsapp.net', 'media.fuio6-2.fna.whatsapp.net', 'skip_forced_signaling', 'dleq_proof', 
        'status_video_max_bitrate', 'lazy_send_probing_req', 'enhanced_storage_management', 
        'android_privatestats_endpoint_dit_enabled', 'media.fscl13-2.fna.whatsapp.net', 'video_duration'
    ],
    [
        'group_call_discoverability_enabled', 'media.faep9-2.fna.whatsapp.net', 'msgr', 
        'bloks_loggedin_access_app_id', 'signing_cert', 'audio_nack_max_buffer_time', 
        'upload_retries', 'media.fdav2-2.fna.whatsapp.net', 'facebook_captcha_v1', 
        'file_overwrite_allowed', 'video_max_duration', 'low_bandwidth', 'mms_cache_eviction_enabled', 
        'mms_timing', 'feature_settings', 'media.fpcp2-1.fna.whatsapp.net', 'audio_nack_max_recoverable_delay', 
        'source', 'fallback', 'gallery', 'video_playback', 'enabled', 'timeout_value', 
        'fixed_gain_value', 'media.fmg5-1.fna.whatsapp.net', 'unlimited', 'false', 'full_screen', 
        'video_control_bar', 'queue_length', 'audio_quality', 'screen_capture', 'max_session_duration', 
        'reduce_jb', 'audio_quality_threshold', 'full_session_expiry', 'localization', 
        'volume_level', 'true', 'next', 'vibration', 'transcode_max_bitrate', 'media file', 'version', 
        'app_id', 'locale', 'capping', 'active', 'text', 'media.frrh2-1.fna.whatsapp.net', 
        'message_interval', 'sync_audio', 'restricted_mode', 'error', 'playback', 'cut_off', 
        'h.264_profile', 'app_instance_id', 'media.fmt7-1.fna.whatsapp.net', 'auto', 'media.fjhb2-2.fna.whatsapp.net', 
        'enable_http2', 'admin_access', 'network_error', 'duration_limit', 'resolution', 
        'media.fcpx2-2.fna.whatsapp.net', 'video_enable_decrypt', 'video_enable_hdr', 
        'media.fxy6-1.fna.whatsapp.net', 'force_mode', 'e2ee', 'mediav1', 'media.fcpx1-1.fna.whatsapp.net', 
        'media.fhhy1-1.fna.whatsapp.net', 'audio_protection', '2x', 'audio_latency', 'mp4', 
        'media.fsu6-2.fna.whatsapp.net', 'web_auth_enabled', 'media.fxh2-1.fna.whatsapp.net', '12', 
        'media.fsd5-2.fna.whatsapp.net', 'enable_fp_auth', '24', 'data_too_large', 'audio_sync', 
        'media.fqho1-2.fna.whatsapp.net', 'title', 'release', 'media.fpnq5-1.fna.whatsapp.net', 
        'media.fjgb2-2.fna.whatsapp.net', 'player', 'locked', 'captions', 'no', 'media.kkp2-1.fna.whatsapp.net', 
        'encoder', 'output', 'active_mms', 'media.fqna1-1.fna.whatsapp.net', 'off', 'audio_max_session_duration', 
        'video_timing', 'audio_transcode_enabled', 'media.fuw4-1.fna.whatsapp.net', 'media.frv1-2.fna.whatsapp.net', 
        'fb', 'audio_max_duration', 'video', 'audio_extra', 'media.fiwo2-1.fna.whatsapp.net', 
        'video_max_size', 'media.fjge5-1.fna.whatsapp.net', 'media.fif1-1.fna.whatsapp.net', 
        'media.fpat2-1.fna.whatsapp.net', 'privacy', 'audio_max_size', '6.0', 
        'audio_protect', 'media.fsw2-2.fna.whatsapp.net', '4', 'default', '2', 'enable_audio_level_adjustment', 
        'enabled', 'media.gty6-1.fna.whatsapp.net', 'phone_type', 'media.fiwo1-1.fna.whatsapp.net', 
        'media.ftcd4-2.fna.whatsapp.net', '9.0', 'video_level', 'volume', 'cache', 'short', 
        'media.fpnw1-1.fna.whatsapp.net', 'media.fmbd3-1.fna.whatsapp.net', 'content_type', 
        'privacy_settings', 'output_max_size', 'off', 'camera', 'audio_encoding', 'audio_bitrate', 
        'media.fepp1-2.fna.whatsapp.net', '1080p', 'output_max_duration', 'media.fzjd1-1.fna.whatsapp.net', 
        'audio_encode_quality', 'device', 'media.fhbg1-1.fna.whatsapp.net', 'video_max_height', 
        'media.fnv9-1.fna.whatsapp.net', 'audio_max_bitrate', 'media.fmd6-2.fna.whatsapp.net', 
        'media.fau1-2.fna.whatsapp.net', 'audio_streaming', 'media.fxs1-1.fna.whatsapp.net', 
        'media.fjmk1-1.fna.whatsapp.net', 'media.fhe7-1.fna.whatsapp.net', '9', 'media.fprw1-2.fna.whatsapp.net', 
        'audio_bit_rate', 'media.fhn3-2.fna.whatsapp.net', 'web_video_optimization', 'image_capture', 
        'video_timing_interval', 'stream', 'video_quality', '3', 'media.frs2-1.fna.whatsapp.net', 
        'media.fsh2-2.fna.whatsapp.net', 'audio_max', 'status', 'media.fvx1-1.fna.whatsapp.net', 
        'volume_level', 'media.fsd5-2.fna.whatsapp.net', 'enable_rtp_audio', 'video_timing_update', 
        'media.fpx1-1.fna.whatsapp.net', 'media.fngd1-2.fna.whatsapp.net', '17', 'audio_features', 
        'media.fnd5-2.fna.whatsapp.net', 'video_timing_optimization', '5.0', 'media.fcx1-1.fna.whatsapp.net', 
        'media.fkm2-1.fna.whatsapp.net', 'stream_audio', 'media.frs3-1.fna.whatsapp.net', 
        'media.fud1-1.fna.whatsapp.net', 'video_update', '5', 'media.fvgh2-1.fna.whatsapp.net', 
        'media.fsg2-2.fna.whatsapp.net', 'video_status', 'media.fgn1-2.fna.whatsapp.net', 'audio_bitrate', 
        'media.fmw5-1.fna.whatsapp.net', 'media.fmp2-2.fna.whatsapp.net', 'media.fgb7-2.fna.whatsapp.net', 
        'camera_feature', 'media.fnd6-1.fna.whatsapp.net', 'true', 'audio_device', 'media.fgbs2-2.fna.whatsapp.net', 
        'fb', 'feature', '9', 'mms_video_max_bitrate', 'media.fsg1-1.fna.whatsapp.net', 
        'media.fr7-2.fna.whatsapp.net', 'audio_max_audio_channels', '1', 'media.fk2-1.fna.whatsapp.net', 
        'video_timing', 'media.fk8-1.fna.whatsapp.net', 'audio_timing', '120', 'audio_transcode_max_bitrate', 
        'true', 'web_messaging', '15', '2', 'media.fmt1-2.fna.whatsapp.net', 'audio_duration', 'video_max_resolution', 
        'media.fsw2-1.fna.whatsapp.net', 'audio_enable', 'media.fsh3-2.fna.whatsapp.net', 'video_transcoding', 
        'media.fkw2-1.fna.whatsapp.net', 'video_enable', 'media.fpm2-1.fna.whatsapp.net', 
        'mms_audio_streaming', 'audio_max', 'audio_nack_policy', 'media.fsd6-1.fna.whatsapp.net', 
        'video_max_size', 'mms_audio_duration_limit', '5', 'media.fst4-1.fna.whatsapp.net', 
        'media.fsp2-2.fna.whatsapp.net', 'status_update', 'media.fcnq5-1.fna.whatsapp.net', 'min'
    ],
]

    @staticmethod
    def generate_token_map():
        token_map = {}

        # Add SINGLE_BYTE_TOKENS to TOKEN_MAP
        for index, token in enumerate(BinaryNodeCodingOptions.SINGLE_BYTE_TOKENS):
            if token:
                token_map[token] = {'index': index}

        # Add DOUBLE_BYTE_TOKENS to TOKEN_MAP if available
        for i, dict_tokens in enumerate(BinaryNodeCodingOptions.DOUBLE_BYTE_TOKENS):
            for j, token in enumerate(dict_tokens):
                token_map[token] = {'dict': i, 'index': j}

        return token_map

    TOKEN_MAP = generate_token_map()
