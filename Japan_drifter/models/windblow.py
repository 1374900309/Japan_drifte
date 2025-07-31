
import logging; logger = logging.getLogger(__name__)
from opendrift.models.basemodel import OpenDriftSimulation
from opendrift.elements.passivetracer import PassiveTracer


class WindBlow(OpenDriftSimulation):
    """Demonstration trajectory model based on OpenDrift framework.

    Simply advects a particle (passive tracer with
    no properties except for position) with the ambient wind.
    """

    ElementType = PassiveTracer
    required_variables = {
        'x_wind': {'fallback': 0},
        'y_wind': {'fallback': 0}
        }


    def __init__(self, *args, **kwargs):
        super(WindBlow, self).__init__(*args, **kwargs)
        self._set_config_default('drift:max_speed', 12)

    def update(self):

        # Simply move particles with ambient wind
        self.update_positions(self.environment.x_wind,
                              self.environment.y_wind)
