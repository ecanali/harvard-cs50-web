document.addEventListener('DOMContentLoaded', function() {
  // Use buttons to toggle between views
  document.querySelector('#inbox').addEventListener('click', () => load_mailbox('inbox'));
  document.querySelector('#sent').addEventListener('click', () => load_mailbox('sent'));
  document.querySelector('#archived').addEventListener('click', () => load_mailbox('archive'));
  document.querySelector('#compose').addEventListener('click', compose_email);
  document.querySelector('#compose-form').addEventListener('submit', send_email);

  // By default, load the inbox
  load_mailbox('inbox');
});

function compose_email() {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-details').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Clear out composition fields
  document.querySelector('#compose-recipients').value = '';
  document.querySelector('#compose-subject').value = '';
  document.querySelector('#compose-body').value = '';
}

function load_mailbox(mailbox) {
  // Show the mailbox and hide other views
  document.querySelector('#emails-view').style.display = 'block';
  document.querySelector('#email-details').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';

  // Show the mailbox name
  document.querySelector('#emails-view').innerHTML = `<h3>${mailbox.charAt(0).toUpperCase() + mailbox.slice(1)}</h3>`;

  // Load the latest emails
  fetch(`/emails/${mailbox}`)
  .then(response => response.json())
  .then(emails => {
    // Display the emails ...
    emails.forEach(email => {
      const element = document.createElement('div');
      if (email.read === true) {
        element.classList.add('read-email');
      }
      const sender = document.createElement('div')
      sender.innerHTML = email.sender
      element.append(sender);
      const subject = document.createElement('div')
      subject.innerHTML = email.subject
      element.append(subject);
      const timestamp = document.createElement('div')
      timestamp.innerHTML = email.timestamp
      element.append(timestamp);
      element.addEventListener('click', function() {
        show_email(email.id);
      });
      document.querySelector('#emails-view').append(element);
    });
  });
}

function show_email(email_id) {
  // Show emails details and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'none';
  document.querySelector('#email-details').style.display = 'block';

  // Clear out last email details
  if (document.querySelector('#email-details').hasChildNodes() === true) {
    document.querySelector('#email-details').innerHTML = "";
  }

  // Load email details
  fetch(`/emails/${email_id}`)
  .then(response => response.json())
  .then(email => {
    // Display email details
    const element = document.createElement('div');

    const sender = document.createElement('div');
    sender.innerHTML = `<strong>From:</strong> ${email.sender}`;
    element.append(sender);

    const recipients = document.createElement('div');
    recipients.innerHTML = `<strong>To:</strong> ${email.recipients.join(', ')}`;
    element.append(recipients);

    const subject = document.createElement('div');
    subject.innerHTML = `<strong>Subject:</strong> ${email.subject}`;
    element.append(subject);

    const timestamp = document.createElement('div');
    timestamp.innerHTML = `<strong>Timestamp:</strong> ${email.timestamp}`;
    element.append(timestamp);

    const reply_button = document.createElement('button');
    reply_button.innerHTML = 'Reply';
    reply_button.setAttribute('id', 'reply');
    reply_button.className = 'btn btn-sm btn-outline-primary';
    element.append(reply_button);

    // Archive/unarchive special logic
    const archive_button = document.createElement('button');
    if (email.archived === false) {
      archive_button.innerHTML = 'Archive';
    } else {
      archive_button.innerHTML = 'Unarchive';
    }
    archive_button.setAttribute('id', 'archive');
    archive_button.dataset.emailid = email_id;
    archive_button.className = 'btn btn-sm btn-outline-primary';
    element.append(archive_button);

    document.querySelector('#email-details').append(element);

    element.append(document.createElement('hr'));

    const body = document.createElement('div');
    body.innerHTML = email.body
    element.append(body);

    // Mark as read
    if (email.read === false) {
      fetch(`/emails/${email_id}`, {
        method: 'PUT',
        body: JSON.stringify({
            read: true
        })
      });
    }

    // Listens click if user wants to archive/unarchive/reply mail
    document.querySelector('#archive').addEventListener('click', archive_email);
    document.querySelector('#reply').addEventListener('click', () => reply_email(email));
  });
}

function archive_email() {
  const email_id = document.querySelector('#archive').dataset.emailid

  fetch(`/emails/${parseInt(email_id)}`)
  .then(response => response.json())
  .then(email => {
    if (email.archived === false) {
      fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: true
        })
      });
    } else {
      fetch(`/emails/${email.id}`, {
        method: 'PUT',
        body: JSON.stringify({
          archived: false
        })
      });
    }
  })

  // Waits 0.2s to update db before load the page
  setTimeout(function () {
    load_mailbox('inbox');
  }, 200);
}

function reply_email(email) {
  // Show compose view and hide other views
  document.querySelector('#emails-view').style.display = 'none';
  document.querySelector('#email-details').style.display = 'none';
  document.querySelector('#compose-view').style.display = 'block';

  // Change the compose view name
  document.querySelector('#compose-view').firstElementChild.innerHTML = "Reply Email";

  // Pre-fill the recipient field with original sender email
  document.querySelector('#compose-recipients').value = `${email.sender}`;

  // Pre-fill the subject adding "Re: " when necessary
  if (email.subject.includes("Re: ")) {
    document.querySelector('#compose-subject').value = `${email.subject}`;
  } else {
    document.querySelector('#compose-subject').value = `Re: ${email.subject}`;
  }

  // Pre-fill the body with original message infos
  document.querySelector('#compose-body').value = `\n\nOn ${email.timestamp} ${email.sender} wrote: \n${email.body}`;
}

function send_email(event) {
  // Prevent default behavior of page reloading after submitting
  event.preventDefault();

  fetch('/emails', {
    method: 'POST',
    body: JSON.stringify({
        recipients: document.querySelector('#compose-recipients').value,
        subject: document.querySelector('#compose-subject').value,
        body: document.querySelector('#compose-body').value
    })
  })
  .then(() => {
    load_mailbox('sent');
  });
}
