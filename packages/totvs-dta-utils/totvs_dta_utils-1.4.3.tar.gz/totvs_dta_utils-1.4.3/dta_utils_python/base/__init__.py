from .api import DtaProxy


class DtaRoutes:
    """
    DTA Base API groups
    """
    def __init__(self, **kwargs):
        """
        Initialize the DtaRoutes class with optional keyword arguments.

        Parameters:
            **kwargs: Optional keyword arguments to initialize the class.
        """
        self.organization = kwargs.get('organization', None)
        self.project = kwargs.get('project', None)
        self.authorization = kwargs.get('authorization', None)
        self.dta_authorization = kwargs.get('dta_authorization', None)

    # DtaProxy management
    def proxy(self):
        return DtaProxy(
            organization=self.organization,
            project=self.project,
            authorization=self.authorization,
            dta_authorization=self.dta_authorization,
        )


class DtaClient(DtaRoutes):

    def __init__(self,
                 project: str = None,
                 organization: str = None,
                 authorization: str = None,
                 dta_authorization: str = None,
                 **kwargs):
        """
        Initialize the DtaBase client class with optional keyword arguments.

        Parameters:
            **kwargs: Optional keyword arguments to initialize the class.
        """
        super().__init__(
            project=project,
            organization=organization,
            authorization=authorization,
            dta_authorization=dta_authorization,
            **kwargs)
