import asyncio

FILTER_DEFAULTS = {
    'karaoke': {'level': 1, 'monoLevel': 1, 'filterBand': 220, 'filterWidth': 100},
    'timescale': {'speed': 1, 'pitch': 1, 'rate': 1},
    'tremolo': {'frequency': 2, 'depth': 0.5},
    'vibrato': {'frequency': 2, 'depth': 0.5},
    'rotation': {'rotationHz': 0},
    'distortion': {'sinOffset': 0, 'sinScale': 1, 'cosOffset': 0, 'cosScale': 1, 'tanOffset': 0, 'tanScale': 1, 'offset': 0, 'scale': 1},
    'channelMix': {'leftToLeft': 1, 'leftToRight': 0, 'rightToLeft': 0, 'rightToRight': 1},
    'lowPass': {'smoothing': 20}
}

def _shallow_equal_with_defaults(current, defaults, override):
    if not current:
        return False
    return all(current.get(k) == override.get(k, defaults[k]) for k in defaults)

def _equalizer_equal(a, b):
    a = a or []
    b = b or []
    if a is b:
        return True
    if len(a) != len(b):
        return False
    return all(x['band'] == b[i]['band'] and x['gain'] == b[i]['gain'] for i, x in enumerate(a))

class Filters:
    def __init__(self, player, options={}):
        self.player = player
        self._pending_update = False

        self.filters = {
            'volume': options.get('volume', 1),
            'equalizer': options.get('equalizer', []),
            'karaoke': options.get('karaoke'),
            'timescale': options.get('timescale'),
            'tremolo': options.get('tremolo'),
            'vibrato': options.get('vibrato'),
            'rotation': options.get('rotation'),
            'distortion': options.get('distortion'),
            'channelMix': options.get('channelMix'),
            'lowPass': options.get('lowPass')
        }

        self.presets = {
            'bassboost': options.get('bassboost'),
            'slowmode': options.get('slowmode'),
            'nightcore': options.get('nightcore'),
            'vaporwave': options.get('vaporwave'),
            '_8d': options.get('_8d')
        }

    def _set_filter(self, filter_name, enabled, options={}):
        current = self.filters.get(filter_name)
        if not enabled:
            if current is None:
                return self
            self.filters[filter_name] = None
            return self._schedule_update()
        
        defaults = FILTER_DEFAULTS[filter_name]
        if current and _shallow_equal_with_defaults(current, defaults, options):
            return self
        
        self.filters[filter_name] = {**defaults, **options}
        return self._schedule_update()

    def _schedule_update(self):
        if self._pending_update:
            return self
        self._pending_update = True
        asyncio.create_task(self._update_filters_task())
        return self

    async def _update_filters_task(self):
        self._pending_update = False
        try:
            await self.update_filters()
        except Exception:
            pass

    def set_equalizer(self, bands):
        next_bands = bands or []
        if _equalizer_equal(self.filters['equalizer'], next_bands):
            return self
        self.filters['equalizer'] = next_bands
        return self._schedule_update()

    def set_karaoke(self, enabled, options={}):
        return self._set_filter('karaoke', enabled, options)

    def set_timescale(self, enabled, options={}):
        return self._set_filter('timescale', enabled, options)

    def set_tremolo(self, enabled, options={}):
        return self._set_filter('tremolo', enabled, options)

    def set_vibrato(self, enabled, options={}):
        return self._set_filter('vibrato', enabled, options)

    def set_rotation(self, enabled, options={}):
        return self._set_filter('rotation', enabled, options)

    def set_distortion(self, enabled, options={}):
        return self._set_filter('distortion', enabled, options)

    def set_channel_mix(self, enabled, options={}):
        return self._set_filter('channelMix', enabled, options)

    def set_low_pass(self, enabled, options={}):
        return self._set_filter('lowPass', enabled, options)

    def set_bassboost(self, enabled, options={}):
        if not enabled:
            if self.presets['bassboost'] is None:
                return self
            self.presets['bassboost'] = None
            return self.set_equalizer([])
        
        value = options.get('value', 5)
        if not 0 <= value <= 5:
            raise ValueError('Bassboost value must be between 0 and 5')
        if self.presets['bassboost'] == value:
            return self
        
        self.presets['bassboost'] = value
        gain = (value - 1) * (1.25 / 9) - 0.25
        eq = [{'band': i, 'gain': gain} for i in range(13)]
        return self.set_equalizer(eq)

    def set_slowmode(self, enabled, options={}):
        rate = options.get('rate', 0.8) if enabled else 1
        timescale = self.filters.get('timescale')
        if self.presets['slowmode'] == enabled and timescale and timescale.get('rate') == rate:
            return self
        self.presets['slowmode'] = enabled
        return self.set_timescale(enabled, {'rate': rate})

    def set_nightcore(self, enabled, options={}):
        rate = options.get('rate', 1.5) if enabled else 1
        timescale = self.filters.get('timescale')
        if self.presets['nightcore'] == enabled and timescale and timescale.get('rate') == rate:
            return self
        self.presets['nightcore'] = enabled
        return self.set_timescale(enabled, {'rate': rate})

    def set_vaporwave(self, enabled, options={}):
        pitch = options.get('pitch', 0.5) if enabled else 1
        timescale = self.filters.get('timescale')
        if self.presets['vaporwave'] == enabled and timescale and timescale.get('pitch') == pitch:
            return self
        self.presets['vaporwave'] = enabled
        return self.set_timescale(enabled, {'pitch': pitch})

    def set_8d(self, enabled, options={}):
        rotation_hz = options.get('rotationHz', 0.2) if enabled else 0
        rotation = self.filters.get('rotation')
        if self.presets['_8d'] == enabled and rotation and rotation.get('rotationHz') == rotation_hz:
            return self
        self.presets['_8d'] = enabled
        return self.set_rotation(enabled, {'rotationHz': rotation_hz})

    async def clear_filters(self):
        changed = False
        for key, value in self.filters.items():
            new_value = 1 if key == 'volume' else [] if key == 'equalizer' else None
            if value != new_value:
                self.filters[key] = new_value
                changed = True
        
        for key in self.presets:
            if self.presets[key] is not None:
                self.presets[key] = None
        
        if not changed:
            return self
        return await self.update_filters()

    async def update_filters(self):
        await self.player.node.rest.update_player({
            'guildId': self.player.guild_id,
            'data': {'filters': self.filters}
        })
        return self
