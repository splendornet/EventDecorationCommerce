from treebeard.admin import TreeAdmin
from django.http import HttpResponse, HttpResponseBadRequest


class CustomTreeAdmin(TreeAdmin):

    def get_node(self, node_id):

        return self.model.objects.get(pk=node_id)

    def move_node(self, request):
        try:
            node_id = request.POST['node_id']
            target_id = request.POST['sibling_id']
            as_child = bool(int(request.POST.get('as_child', 0)))


        except (KeyError, ValueError):
            # Some parameters were missing return a BadRequest
            return HttpResponseBadRequest('Malformed POST params')

        node = self.get_node(node_id)
        target = self.get_node(target_id)
        is_sorted = True if node.node_order_by else False

        pos = {
            (True, True): 'sorted-child',
            (True, False): 'last-child',
            (False, True): 'sorted-sibling',
            (False, False): 'left',
        }[as_child, is_sorted]
        return self.try_to_move_node(as_child, node, pos, request, target)