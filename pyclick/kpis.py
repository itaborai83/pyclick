class Handler(object):

    def __init__(self):
        pass
    
    def begin(self):
        pass
    
    def new_day(self, date):
        pass
        
    def begin_event(self, row):
        pass
        
    def process_action(self, row):
        pass
    
    def end_event(self, row):
        pass
        
    def end(self):
        pass

    def write_details(self, sheet_name, xw):
        df = self.get_kpi_details()
        df.to_excel(xw, sheet_name=sheet_name, index=False)
        
    def compute_kpi(self):
        raise NotImplementedError
    
    def get_kpi_details(self):
        raise NotImplementedError


class Runner(object):

    def __init__(self, filter=None):
        if filter is None:
            filter = lambda row: True
        self.filter = filter
        self.handlers = []
        self.seen = set()
        self.done = set()
        
    
    def add_handler(self, handler):
        self.handlers.append(handler)
        
    def run(self, df):
        df.sort_values(by='DATA_INICIO_ACAO', inplace=True, kind='mergesort') # mergesort is stable
        self.do_begin()
        last_row = None
        last_date = None
        
        for row in df.itertuples(): 
            assert row.DATA_INICIO_ACAO
            
            if not self.filter(row):
                continue
            
            date = row.DATA_INICIO_ACAO[ 0 : 10 ]
            assert last_date is None or last_date <= date
            
            if last_date is None or date != last_date:
                self.do_new_day(date)
            
            if row.ID_CHAMADO not in self.seen:
                assert row.ID_CHAMADO not in self.done
                self.seen.add(row.ID_CHAMADO)
                self.do_begin_event(row)
                self.do_process_action(row)
                
            
            elif row.ID_CHAMADO in self.seen:
                assert row.ID_CHAMADO not in self.done
                if row.ULTIMA_ACAO == 'n':
                    self.do_process_action(row)    
                elif row.ULTIMA_ACAO == 'y':
                    self.seen.remove(row.ID_CHAMADO)
                    self.done.add(row)
                    self.do_process_action(row)
                    self.do_end_event(row)
                else:
                    assert 1 == 2 # should not happen
            
            else:
                    assert 1 == 2 # should not happen
            last_row = row
            last_date = date
        self.do_end()
    
    def do_begin(self):
        for h in self.handlers:
            h.begin()
    
    def do_new_day(self, date):
        for h in self.handlers:
            h.new_day(date)
    
    def do_begin_event(self, row):
        for h in self.handlers:
            h.begin_event(row)
    
    def do_filter(self, row):
        return self.filter(row)
        
    def do_process_action(self, row):
        for h in self.handlers:
            h.process_action(row)
    
    def do_end_event(self, row):
        for h in self.handlers:
            h.end_event(row)
        
    def do_end(self):
        for h in self.handlers:
            h.end()

            