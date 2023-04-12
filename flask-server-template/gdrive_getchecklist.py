class getChecklist:
    def __init__(self, spreadsheet_id, range_name):
        self.spreadsheet_id = spreadsheet_id
        self.range_name = range_name

    def get_checklist(gdrive):
        self.client = gdrive.client
        self.service = self.client.sheet.service
        self.result = self.service.spreadsheets().values().get(
            spreadsheetId=self.spreadsheet_id, range=self.range_name).execute()
        self.grid_values = self.result['values']
        self.df = pd.DataFrame(grid_values).style.hide_index()
        # df = df.style.hide_index()
        # df.drop(['None'], inplace=True)
        self.html_df = self.df.to_html()
        self.html_df = self.html_df.replace("<table>", "<table class='table table-dark")
        self.resp = render_template_string(self.html_df)
        return self.resp