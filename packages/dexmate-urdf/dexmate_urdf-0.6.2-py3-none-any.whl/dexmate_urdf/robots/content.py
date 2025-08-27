from .paths import RobotModel, RobotType, URDFModel


class F5d6HandModel(RobotModel):
    @property
    def f5d6_right(self) -> URDFModel:
        return URDFModel(self._type, self._name, "f5d6_right")

    @property
    def f5d6_left(self) -> URDFModel:
        return URDFModel(self._type, self._name, "f5d6_left")


class Vega1Model(RobotModel):
    @property
    def vega_upper_body(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega_upper_body")

    @property
    def vega_no_effector(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega_no_effector")

    @property
    def vega_upper_body_no_effector(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega_upper_body_no_effector")

    @property
    def vega(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega")

    @property
    def vega_upper_body_right_arm(self) -> URDFModel:
        return URDFModel(self._type, self._name, "vega_upper_body_right_arm")


class HandsType(RobotType):
    @property
    def f5d6_hand(self) -> F5d6HandModel:
        return F5d6HandModel("hands", "f5d6_hand")


class HumanoidType(RobotType):
    @property
    def vega_1(self) -> Vega1Model:
        return Vega1Model("humanoid", "vega_1")


hands = HandsType("hands")
humanoid = HumanoidType("humanoid")


def get_all_robot_dirs() -> list[RobotModel]:
    return []
