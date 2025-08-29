class NodeTagger:
    """A node tagger allows you to provide a type and content regular expression and then
    tag content in all matching nodes.

    It allows for multiple matching groups to be defined, also the ability to use all content
    and also just tag the node (ignoring the matching groups)
    """

    def __init__(
        self,
        selector,
        tag_to_apply,
        content_re=".*",
        use_all_content=True,
        node_only=False,
        node_tag_uuid=None,
    ):
        self.selector = selector
        """The selector to use to find the node(s) to tag"""
        self.content_re = content_re
        """A regular expression used to match the content in the identified nodes"""
        self.use_all_content = use_all_content
        """A flag that will assume that all content should be tagged (there will be no start/end)"""
        self.tag_to_apply = tag_to_apply
        """The tag to apply to the node(s)"""
        self.node_only = node_only
        """Tag the node only and no content"""
        self.node_tag_uuid = node_tag_uuid
        """The UUID to use on the tag"""

    def process(self, document):
        """ """
        document.content_node.tag(
            selector=self.selector,
            tag_to_apply=self.tag_to_apply,
            content_re=self.content_re,
            use_all_content=self.use_all_content,
            node_only=self.node_only,
            tag_uuid=self.node_tag_uuid,
        )

        return document


class NodeTagger:
    """A node tagger allows you to provide a type and content regular expression and then
    tag content in all matching nodes.

    It allows for multiple matching groups to be defined, also the ability to use all content
    and also just tag the node (ignoring the matching groups)
    """

    def __init__(
        self,
        selector,
        tag_to_apply,
        content_re=".*",
        use_all_content=True,
        node_only=False,
        node_tag_uuid=None,
    ):
        self.selector = selector
        """The selector to use to find the node(s) to tag"""
        self.content_re = content_re
        """A regular expression used to match the content in the identified nodes"""
        self.use_all_content = use_all_content
        """A flag that will assume that all content should be tagged (there will be no start/end)"""
        self.tag_to_apply = tag_to_apply
        """The tag to apply to the node(s)"""
        self.node_only = node_only
        """Tag the node only and no content"""
        self.node_tag_uuid = node_tag_uuid
        """The UUID to use on the tag"""

    def process(self, document):
        """ """
        document.content_node.tag(
            selector=self.selector,
            tag_to_apply=self.tag_to_apply,
            content_re=self.content_re,
            use_all_content=self.use_all_content,
            node_only=self.node_only,
            tag_uuid=self.node_tag_uuid,
        )

        return document


class NodeTagCopy:
    """The NodeTagCopy action allows you select nodes specified by the selector and create copies of the existing_tag (if it exists) with the new_tag_name.
    If a tag with the 'existing_tag_name' does not exist on a selected node, no action is taken for that node.
    """

    def __init__(self, selector, existing_tag_name, new_tag_name):
        self.selector = selector
        """The selector to match the nodes"""
        self.existing_tag_name = existing_tag_name
        """The existing tag name that will be the source"""
        self.new_tag_name = new_tag_name
        """The new tag name that will be the destination"""

    def process(self, document):
        """ """
        document.content_node.copy_tag(
            selector=self.selector,
            existing_tag_name=self.existing_tag_name,
            new_tag_name=self.new_tag_name,
        )
        return document
