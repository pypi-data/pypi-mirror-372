from compas.plugins import plugin


@plugin(category="factories", requires=["compas_pb"])
def register_serializers():
    import compas_timber_pb.data  # noqa: F401

    print("Discovered compas_pb plugin for compas_timber_pb")
