class Motor:
    def __init__(self, ax, enc_axes, ctype, ms=None, index=0, post=None):
        self.axis = ax
        self.enc_axes = enc_axes
        self.ctype = ctype
        self.ms = ms
        self.jdist = 0
        self.index = index
        self.post = post

    def override_jdist_for_phase(self, phase_code):
        pass

    def release_jdist_override(self):
        pass
