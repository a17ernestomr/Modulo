# -*- coding: utf-8 -*-
import logging

from odoo import models, fields, api
from odoo.exceptions import UserError
from odoo.tools.translate import _

logger = logging.getLogger(__name__)


class LibraryBook(models.Model):
    _name = 'library.book'
    _description = 'Library Book'

    name = fields.Char('Title', required=True)
    date_release = fields.Date('Release Date')
    author_ids = fields.Many2many('res.partner', string='Authors')
    category_id = fields.Many2one('library.book.category', string='Category')
    number = fields.Integer('Existencias')
    total_number = fields.Integer('Existencias Totales')
    numBorrowed = fields.Integer('Reservas')
    author_number = fields.Integer(compute='_compute_author_number')

    #book_count = fields.Integer(compute='compute_count')
    #amount_diff = fields.Float("Amoun Diff.", compute='compute_count', compute_sudo=True, store=True, digits=(12, 6), readonly=True)
    state = fields.Selection([
        ('draft', 'Unavailable'),
        ('available', 'Available'),
        ('borrowed', 'Borrowed')],
        'State', default="available")

    @api.model
    def is_allowed_transition(self, old_state, new_state):
        allowed = [('draft', 'available'),
                   ('available', 'borrowed'),
                   ('borrowed', 'available'),
                   ('available', 'lost'),
                   ('borrowed', 'lost'),
                   ('lost', 'available')]
        return (old_state, new_state) in allowed

    def change_state(self, new_state):
        for book in self:
            if book.is_allowed_transition(book.state, new_state):
                if new_state == 'borrowed':
                    if self.number ==1:
                        book.state = new_state    
                else:
                    book.state = new_state        
            else:
                message = _('Moving from %s to %s is not allowd') % (book.state, new_state)
                raise UserError(message)
    
    def devolver(self):
        if self.state == 'available' and self.number<self.total_number:
            self.number +=1


    def make_available(self):
        if self.state == 'borrowed':
            self.number += 1
        self.change_state('available')
        

    def make_borrowed(self):
        self.change_state('borrowed')
        self.number -= 1
        self.numBorrowed += 1

    def make_lost(self):
        #self.change_state('lost')
        if self.number >=2:
             self.number -= 1
        elif self.number == 1:
            self.number = 0
            for book in self:
                book.state = 'borrowed'   

    def log_all_library_members(self):
        library_member_model = self.env['library.member']  # This is an empty recordset of model library.member
        all_members = library_member_model.search([])
        print("ALL MEMBERS:", all_members)
        return True


    def create_categories(self):
        categ1 = {
            'name': 'Novelas de ciencia ficción',
            'description': 'Novelas ambientadas en el futuro'
        }
        categ2 = {
            'name': 'Novelas de terror',
            'description': 'Novelas que generan miedo'
        }
        parent_category_val = {
            'name': 'Acción',
            'description': 'Novelas de acción y suspense',
            'child_ids': [
                (0, 0, categ1),
                (0, 0, categ2),
            ]
        }
        # Total 3 records (1 parent and 2 child) will be craeted in library.book.category model
        record = self.env['library.book.category'].create(parent_category_val)
        return True

    def change_release_date(self):
        self.ensure_one()
        self.date_release = fields.Date.today()

    def delete(self):
        self.ensure_one()
        self.unlink()
        return True


    def find_book(self):
        domain = [
            '|',
                '&', ('name', 'ilike', 'Book Name'),
                     ('category_id.name', '=', 'Category Name'),
                '&', ('name', 'ilike', 'Book Name 2'),
                     ('category_id.name', '=', 'Category Name 2')
        ]
        books = self.search(domain)
        logger.info('Books found: %s', books)
        return True

    # Filter recordset
    def filter_books(self):
        all_books = self.search([])
        filtered_books = self.books_with_multiple_authors(all_books)
        logger.info('Filtered Books: %s', filtered_books)

    @api.model
    def books_with_multiple_authors(self, all_books):
        def predicate(book):
            if len(book.author_ids) > 1:
                return True
        return all_books.filtered(predicate)

    # Traversing recordset
    def mapped_books(self):
        all_books = self.search([])
        books_authors = self.get_author_names(all_books)
        logger.info('Books Authors: %s', books_authors)

    @api.model
    def get_author_names(self, all_books):
        return all_books.mapped('author_ids.name')

    # Sorting recordset
    def sort_books(self):
        all_books = self.search([])
        books_sorted = self.sort_books_by_date(all_books)
        logger.info('Books before sorting: %s', all_books)
        logger.info('Books after sorting: %s', books_sorted)


   
    def get_books(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Books',
            'view_mode': 'form,tree',
            'res_model': 'library.book',
            'domain': [('author_ids', '=', self.id)],
            'context': "{'create': False}"
        }

   # def compute_count(self):
    #    for record in self:
     #       record.book_count = self.env['library.book'].search_count(
      #          [('name', '=', self.id)])



    @api.model
    def sort_books_by_date(self, all_books):
        return all_books.sorted(key='date_release')
    


    @api.depends('author_ids')
    def _compute_author_number(self):
      for rec in self:	
        rec.author_number = len(rec.author_ids)

    
  


  #  @api.multi
   # def associate_account(self):
    # for partner in self:
     #    partner.associate_count = len(partner.author_ids)

class LibraryMember(models.Model):

    _name = 'library.member'
    _inherits = {'res.partner': 'partner_id'}
    _description = "Library member"

    partner_id = fields.Many2one('res.partner', ondelete='cascade')
    date_start = fields.Date('Member Since')
    date_end = fields.Date('Termination Date')
    member_number = fields.Char()
    date_of_birth = fields.Date('Date of birth')
