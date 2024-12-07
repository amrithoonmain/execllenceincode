// DOM Elements
const loginBtn = document.querySelector('.login-btn');
const adminBtn = document.querySelector('.admin-btn');
const loginModal = document.getElementById('loginModal');
const loginForm = document.getElementById('loginForm');
const navLinks = document.querySelectorAll('.nav-links a');
const sections = document.querySelectorAll('section');

// Event Listeners
loginBtn.addEventListener('click', () => {
    loginModal.style.display = 'block';
});

adminBtn.addEventListener('click', () => {
    loginModal.style.display = 'block';
});

loginModal.addEventListener('click', (e) => {
    if (e.target === loginModal) {
        loginModal.style.display = 'none';
    }
});

loginForm.addEventListener('submit', (e) => {
    e.preventDefault();
    // Add login logic here
    loginModal.style.display = 'none';
});

// Navigation
navLinks.forEach(link => {
    link.addEventListener('click', (e) => {
        e.preventDefault();
        console.log(`Link clicked: ${link.getAttribute('href')}`);
        
        // Remove active class from all links
        navLinks.forEach(link => {
            link.parentElement.classList.remove('active');
        });
        
        // Add active class to clicked link
        link.parentElement.classList.add('active');
        
        // Show corresponding section
        const targetId = link.getAttribute('href').substring(1);
        const targetSection = document.getElementById(targetId);
        if (targetSection) {
            console.log(`Target section found: ${targetId}`);
            sections.forEach(section => {
                section.classList.remove('active');
            });
            targetSection.classList.add('active');
        } else {
            console.error(`Section with ID ${targetId} not found`);
        }
    });
});

// Sample data for books
const sampleBooks = [
    {
        id: 1,
        title: "The Great Gatsby",
        author: "F. Scott Fitzgerald",
        year: 1925,
        status: "available"
    },
    {
        id: 2,
        title: "To Kill a Mockingbird",
        author: "Harper Lee",
        year: 1960,
        status: "issued"
    },
    {
        id: 3,
        title: "1984",
        author: "George Orwell",
        year: 1949,
        status: "available"
    }
];

// Function to create book cards
function createBookCard(book) {
    const card = document.createElement('div');
    card.className = 'book-card';
    card.innerHTML = `
        <div class="book-cover">
            <div class="book-spine"></div>
        </div>
        <div class="book-info">
            <h3>${book.title}</h3>
            <p>Author: ${book.author}</p>
            <p>Year: ${book.year}</p>
            <p class="status ${book.status}">${book.status}</p>
            <button class="issue-btn" ${book.status === 'issued' ? 'disabled' : ''} data-id="${book.id}">
                ${book.status === 'issued' ? 'Issued' : 'Issue Book'}
            </button>
        </div>
    `;
    return card;
}

// Function to add a book
function addBook() {
    const bookTitle = prompt("Enter book title:");
    const bookAuthor = prompt("Enter book author:");
    const bookYear = prompt("Enter publication year:");
    if (bookTitle && bookAuthor && bookYear) {
        fetch('/api/books', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                bookId: Date.now(), // Generate a unique ID
                bookName: bookTitle,
                publicationYear: bookYear,
                author: bookAuthor
            })
        })
        .then(response => response.json())
        .then(data => {
            if (data.message === "Book added successfully!") {
                sampleBooks.push({
                    id: data.bookId,
                    title: bookTitle,
                    author: bookAuthor,
                    year: bookYear,
                    status: 'available'
                });
                renderBooks(sampleBooks);
                updateStats();
            } else {
                alert("Error adding book: " + data.error);
            }
        })
        .catch(error => {
            console.error("Error adding book: ", error);
        });
    }
}

// Function to issue a book
function issueBook(bookId) {
    fetch(`/api/books/${bookId}`, {
        method: 'PUT',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            status: 'issued'
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.message === "Book status updated successfully!") {
            const book = sampleBooks.find(book => book.id === bookId);
            if (book) {
                book.status = 'issued';
                renderBooks(sampleBooks);
                updateStats();
            }
        } else {
            alert("Error issuing book: " + data.error);
        }
    })
    .catch(error => {
        console.error("Error issuing book: ", error);
    });
}

// Add event listener to the "Add Book" button
const addBookBtn = document.querySelector('.add-note-btn');
addBookBtn.textContent = 'Add Book';
addBookBtn.addEventListener('click', addBook);

// Add event listener to the "Issue Book" buttons
const booksGrid = document.querySelector('.books-grid');
booksGrid.addEventListener('click', (e) => {
    if (e.target.classList.contains('issue-btn')) {
        const bookId = e.target.dataset.id;
        issueBook(bookId);
    }
});

// Function to render books
function renderBooks(books) {
    const booksGrid = document.querySelector('.books-grid');
    booksGrid.innerHTML = '';
    books.forEach(book => {
        booksGrid.appendChild(createBookCard(book));
    });
}

// Initial render
renderBooks(sampleBooks);

// Search functionality
const searchInput = document.querySelector('.search-bar input');
searchInput.addEventListener('input', (e) => {
    const searchTerm = e.target.value.toLowerCase();
    const filteredBooks = sampleBooks.filter(book => 
        book.title.toLowerCase().includes(searchTerm) ||
        book.author.toLowerCase().includes(searchTerm) ||
        book.id.toString().includes(searchTerm)
    );
    renderBooks(filteredBooks);
});

// Update stats
function updateStats() {
    const totalBooks = sampleBooks.length;
    const issuedBooks = sampleBooks.filter(book => book.status === 'issued').length;
    const availableBooks = totalBooks - issuedBooks;
    
    document.querySelector('.stat-card:nth-child(1) p').textContent = totalBooks;
    document.querySelector('.stat-card:nth-child(3) p').textContent = issuedBooks;
}

// Initial stats update
updateStats();

// Notes functionality
const notesGrid = document.querySelector('.notes-grid');
const addNoteBtn = document.querySelector('.add-note-btn');

addNoteBtn.addEventListener('click', () => {
    const noteTitle = prompt("Enter note title:");
    const noteDescription = prompt("Enter note description:");
    if (noteTitle && noteDescription) {
        const noteCard = document.createElement('div');
        noteCard.className = 'note-card';
        noteCard.innerHTML = `
            <h3>${noteTitle}</h3>
            <p>${noteDescription}</p>
            <button class="delete-note-btn">Delete</button>
        `;
        notesGrid.appendChild(noteCard);

        // Delete note functionality
        noteCard.querySelector('.delete-note-btn').addEventListener('click', () => {
            notesGrid.removeChild(noteCard);
        });
    }
});

// News functionality
const newsArticles = document.querySelector('.news-articles');

function fetchNews() {
    // Sample news articles
    const sampleNews = [
        {
            title: "Library Launches New Digital Services",
            source: "Library News",
            url: "#"
        },
        {
            title: "New Books Added to the Collection",
            source: "Library Updates",
            url: "#"
        }
    ];

    sampleNews.forEach(article => {
        const articleCard = document.createElement('div');
        articleCard.className = 'news-article';
        articleCard.innerHTML = `
            <h4>${article.title}</h4>
            <p>Source: ${article.source}</p>
            <a href="${article.url}" target="_blank">Read more</a>
        `;
        newsArticles.appendChild(articleCard);
    });
}

// Fetch news on load
fetchNews();

// Wikipedia functionality
const wikiSearchInput = document.querySelector('.wiki-search input');
const wikiResults = document.querySelector('.wiki-results');

document.querySelector('.search-wiki-btn').addEventListener('click', () => {
    const keyword = wikiSearchInput.value;
    if (keyword) {
        fetchWikipediaArticles(keyword);
    }
});

function fetchWikipediaArticles(keyword) {
    // Sample Wikipedia articles
    const sampleWikiArticles = [
        {
            title: "Digital Library",
            summary: "A digital library is a library that provides access to digital content.",
            url: "#"
        },
        {
            title: "Library Science",
            summary: "Library science is the study of how to manage libraries.",
            url: "#"
        }
    ];

    wikiResults.innerHTML = '';
    sampleWikiArticles.forEach(article => {
        const articleCard = document.createElement('div');
        articleCard.className = 'wiki-article';
        articleCard.innerHTML = `
            <h4>${article.title}</h4>
            <p>${article.summary}</p>
            <a href="${article.url}" target="_blank">Read more</a>
        `;
        wikiResults.appendChild(articleCard);
    });
}
