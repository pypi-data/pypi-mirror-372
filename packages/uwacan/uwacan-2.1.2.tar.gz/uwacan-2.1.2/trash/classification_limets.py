class ClassificationLimit:
    def __init__(self, *limits, is_density, is_monopole):
        self.limits = limits
        self.is_density = is_density
        self.is_monopole = is_monopole

    def __call__(self, frequency, density=True, monopole=False):
        frequency = np.asarray(frequency).astype(float)
        conditions = [
            (limit.f_low <= frequency) & (frequency <= limit.f_high)
            for limit in self.limits
        ]
        limits = [limit.limit for limit in self.limits] + [np.nan]
        levels = np.piecewise(frequency, conditions, limits)

        # TODO: this only works if everything is in thirdoctavebands
        if self.is_density and not density:
            levels += 10 * np.log10((2**(1/6) - 2**(-1/6)) * frequency)
        elif not density:
            levels -= 10 * np.log10((2**(1/6) - 2**(-1/6)) * frequency)

        return levels

    def lloyd_mirror_compensation(self, frequency, depth, angle):
        denom = 4 * np.pi * frequency * depth + np.sin(np.radians(angle) / 1500)
        return np.maximum(0, 10 * np.log10(0.5 + 1 / denom**2))

bureau_veritas_controlled = ClassificationLimit(
    limit(10, 50, lambda f: 169 - 2 * np.log10(f)),
    limit(50, 1e3, lambda f: 165.6 - 20 * np.log10(f / 50)),
    limit(1e3, 50e3, lambda f: 139.6 - 20 * np.log10(f / 1000)),
    is_density=True, is_monopole=False,
)

bureau_veritas_controlled = ClassificationLimit(
    limit(10, 50, lambda f: 169 - 2 * np.log10(f)),
    limit(50, 1e3, lambda f: 165.6 - 20 * np.log10(f / 50)),
    limit(1e3, 50e3, lambda f: 139.6 - 20 * np.log10(f / 1000)),
    is_density=True, is_monopole=False,
)
