import logging

from netbox.plugins import PluginTemplateExtension

from ipfabric_netbox.models import IPFabricSnapshot

logger = logging.getLogger("ipfabric_netbox.template_content")


class SiteTopologyButtons(PluginTemplateExtension):
    model = "dcim.site"

    def buttons(self):
        try:
            site = self.context.get("object")
            source = None
            for snapshot in IPFabricSnapshot.objects.all():
                # `Site.name` is unique in DB, so we can use it to match against IPF snapshots
                if site.name in snapshot.sites:
                    source = snapshot.source
            return self.render(
                "ipfabric_netbox/inc/site_topology_button.html",
                extra_context={"source": source},
            )
        except Exception as e:
            logger.error(f"Could not render topology button: {e}.")
            return "render error"


template_extensions = [SiteTopologyButtons]
